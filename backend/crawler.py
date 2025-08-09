import asyncio
import httpx
from bs4 import BeautifulSoup
import trafilatura
from langdetect import detect
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import aiofiles
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser
import ipaddress
import random
from database import Database
from logging_utils import log_manager

class WebCrawler:
    def __init__(self):
        self.db = Database()
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage")
        self.is_running = False
        self.current_task_id = None
        # settings
        self.user_agent = os.getenv("CRAWLER_USER_AGENT", "ServerAI Knowledge Engine Bot 1.0")
        self.delay_seconds = float(os.getenv("CRAWLER_DELAY", "2"))
        self.timeout = int(os.getenv("CRAWLER_TIMEOUT", "30"))
        self.respect_robots = os.getenv("CRAWLER_RESPECT_ROBOTS", "true").lower() == "true"
        self.max_pages_per_site = int(os.getenv("CRAWLER_MAX_PAGES", "50"))
        self._robots_cache: Dict[str, robotparser.RobotFileParser] = {}
        self._client: Optional[httpx.AsyncClient] = None
        
        # Topic categories and keywords
        self.topic_mapping = {
            "linux": ["linux", "ubuntu", "centos", "debian", "rhel", "bash", "shell"],
            "networking": ["network", "tcp", "ip", "dns", "dhcp", "vpn", "firewall"],
            "mysql": ["mysql", "mariadb", "database", "sql", "innodb"],
            "apache": ["apache", "httpd", "mod_rewrite", "virtual host"],
            "security": ["security", "ssl", "tls", "encryption", "vulnerability"],
            "dns": ["dns", "bind", "nameserver", "domain", "zone"],
            "vmware": ["vmware", "esxi", "vcenter", "virtualization"],
            "cloud": ["aws", "azure", "gcp", "cloud", "ec2", "s3"],
            "email": ["email", "postfix", "exim", "dovecot", "smtp"],
            "web_troubleshooting": ["troubleshoot", "debug", "error", "performance"],
            "vulnerabilities": ["cve", "exploit", "patch", "malware", "rootkit"]
        }
        
        # Default crawl targets
        self.crawl_targets = [
            "https://www.digitalocean.com/community/tutorials",
            "https://linuxize.com",
            "https://www.tecmint.com",
            "https://www.howtoforge.com",
            "https://www.cyberciti.biz",
            "https://wiki.archlinux.org",
            "https://ubuntu.com/server/docs"
        ]

    async def get_status(self):
        """Get current crawler status"""
        return {
            "is_running": self.is_running,
            "task_id": self.current_task_id,
            "progress": await self._get_progress(),
            "sites_crawled": await self._get_sites_crawled(),
            "pages_found": await self._get_pages_found(),
            "last_update": await self._get_last_update()
        }

    async def start_crawl(self):
        """Start a new crawl task"""
        if self.is_running:
            raise Exception("Crawler is already running")
        
        task_id = str(uuid.uuid4())
        self.current_task_id = task_id
        self.is_running = True
        
        await self.db.create_crawl_task(task_id, "started")
        return task_id

    async def stop_crawl(self):
        """Stop the current crawl"""
        self.is_running = False
        if self.current_task_id:
            await self.db.update_crawl_task(self.current_task_id, "stopped")
        self.current_task_id = None

    async def run_crawl(self, task_id: str):
        """Execute the crawling process with robots/TOS compliance and logging"""
        try:
            await self.db.update_crawl_task(task_id, "running")
            await self._log("crawl.start", task_id=task_id)
            client = await self._get_client()

            total = len(self.crawl_targets)
            for i, target in enumerate(self.crawl_targets):
                if not self.is_running:
                    break

                await self._log("site.begin", url=target, idx=i + 1, total=total)
                await self._crawl_site(target)

                # Update progress
                progress = ((i + 1) / total) * 100
                await self.db.update_crawl_progress(task_id, progress)
                await self._log("progress", value=progress)

                # Small polite delay between sites
                await asyncio.sleep(1.0)

            await self.db.update_crawl_task(task_id, "completed")
            await self._log("crawl.complete")
        except Exception as e:
            await self._log("crawl.error", error=str(e))
            await self.db.update_crawl_task(task_id, "failed")
        finally:
            self.is_running = False
            self.current_task_id = None
            # close client
            try:
                if self._client:
                    await self._client.aclose()
            except Exception:
                pass

    async def _crawl_site(self, base_url: str):
        """Crawl a specific site (same-domain only) with robots compliance"""
        parsed = urlparse(base_url)
        base_netloc = parsed.netloc
        rp = await self._get_robots(base_url)
        client = await self._get_client()

        # check base_url allowed
        if not self._allowed_by_robots(rp, base_url):
            await self._log("robots.disallow", url=base_url)
            return

        try:
            resp = await client.get(base_url)
            if resp.status_code >= 400:
                await self._log("site.error", url=base_url, status=resp.status_code)
                return
            ctype = resp.headers.get("content-type", "")
            if "text/html" not in ctype:
                await self._log("site.skip", url=base_url, reason="non-html")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')
            links_set = set()
            for a in soup.find_all('a', href=True):
                rel = a.get('rel') or []
                # skip nofollow links
                if isinstance(rel, list) and any(r.lower() == 'nofollow' for r in rel):
                    continue
                href = a['href']
                abs_url = urljoin(base_url, href)
                if self._is_safe_url(abs_url, base_netloc):
                    links_set.add(abs_url)

            links = list(links_set)[: self.max_pages_per_site]
            await self._log("site.links", url=base_url, count=len(links))

            sem = asyncio.Semaphore(5)

            async def process_link(link_url: str):
                if not self.is_running:
                    return
                if not self._allowed_by_robots(rp, link_url):
                    await self._log("robots.disallow", url=link_url)
                    return
                await self._sleep_with_delay(rp)

                backoff = 1.0
                for attempt in range(3):
                    try:
                        r = await client.get(link_url)
                        status = r.status_code
                        if status == 429 or status == 403:
                            await self._log("fetch.backoff", url=link_url, status=status, attempt=attempt+1)
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        if status >= 400:
                            await self._log("fetch.error", url=link_url, status=status)
                            return
                        # type/length guards
                        ctype = r.headers.get("content-type", "")
                        if "text/html" not in ctype:
                            await self._log("page.skip", url=link_url, reason="non-html")
                            return
                        clen = r.headers.get("content-length")
                        if clen and int(clen) > 1_000_000:
                            await self._log("page.skip", url=link_url, reason="too-large")
                            return

                        # meta robots noindex/nofollow
                        psoup = BeautifulSoup(r.text, 'html.parser')
                        meta = psoup.find('meta', attrs={'name': 'robots'})
                        if meta and meta.get('content'):
                            content = meta['content'].lower()
                            if 'noindex' in content or 'nofollow' in content:
                                await self._log("robots.meta-skip", url=link_url)
                                return

                        await self._process_page(link_url, html=r.text)
                        return
                    except Exception as e:
                        await self._log("fetch.exception", url=link_url, error=str(e), attempt=attempt+1)
                        await asyncio.sleep(backoff)
                        backoff *= 2

            tasks = []
            for link in links:
                await sem.acquire()
                tasks.append(asyncio.create_task(process_link(link)))
                sem.release()
            # process sequentially but scheduled, keep minimal complexity
            for t in tasks:
                await t

            await self._log("site.complete", url=base_url)
        except Exception as e:
            await self._log("site.exception", url=base_url, error=str(e))

    async def _process_page(self, url: str, html: Optional[str] = None):
        """Process and classify a single page"""
        try:
            # Extract clean text (avoid network fetch if html provided)
            if html is None:
                downloaded = await asyncio.to_thread(trafilatura.fetch_url, url)
            else:
                downloaded = html
            if not downloaded:
                await self._log("extract.skip", url=url, reason="no-content")
                return

            text = await asyncio.to_thread(trafilatura.extract, downloaded)
            if not text or len(text) < 500:  # Skip short pages
                await self._log("extract.skip", url=url, reason="too-short")
                return
            
            # Detect language
            try:
                lang = detect(text)
                if lang != 'en':
                    await self._log("extract.skip", url=url, reason="non-english", lang=lang)
                    return  # Skip non-English content
            except Exception as e:
                await self._log("extract.skip", url=url, reason="lang-detect-failed", error=str(e))
                return
            
            # Classify topic
            topic = self._classify_topic(text, url) or "general"
            
            # Save to database
            await self.db.save_article(url, text, topic)
            await self._log("page.saved", url=url, topic=topic)
            
            # Save to file
            await self._save_to_file(url, text, topic)
            
        except Exception as e:
            await self._log("page.exception", url=url, error=str(e))

    def _classify_topic(self, text: str, url: str) -> Optional[str]:
        """Classify content into topic categories"""
        text_lower = text.lower()
        url_lower = url.lower()
        
        # Score each topic
        topic_scores = {}
        for topic, keywords in self.topic_mapping.items():
            score = 0
            for keyword in keywords:
                score += text_lower.count(keyword)
                score += url_lower.count(keyword) * 2  # URL keywords are more important
            topic_scores[topic] = score
        
        # Return topic with highest score (if above threshold)
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[best_topic] > 2:  # Minimum threshold
                return best_topic
        
        return None

    async def _save_to_file(self, url: str, content: str, topic: str):
        """Save content to organized file structure"""
        # Create topic directory
        topic_dir = os.path.join(self.storage_path, topic)
        os.makedirs(topic_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = url.split("//")[1].split("/")[0].replace(".", "_")
        filename = f"{timestamp}_{domain}.md"
        
        # Create content with metadata
        file_content = f"""# {url}

**Source:** {url}
**Topic:** {topic}
**Crawled:** {datetime.now().isoformat()}

---

{content}
"""
        
        # Save file
        file_path = os.path.join(topic_dir, filename)
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(file_content)

    async def _get_progress(self):
        """Get current crawl progress"""
        if not self.current_task_id:
            return 0
        return await self.db.get_crawl_progress(self.current_task_id)

    async def _get_sites_crawled(self):
        """Get number of sites crawled"""
        return await self.db.get_sites_crawled()

    async def _get_pages_found(self):
        """Get total pages found"""
        return await self.db.get_total_articles()

    async def _get_last_update(self):
        """Get last update timestamp"""
        return await self.db.get_last_update()

    async def _log(self, event_type: str, **data):
        await log_manager.publish({
            "type": event_type,
            "task_id": self.current_task_id,
            **data,
        })

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en",
                },
                follow_redirects=True,
            )
        return self._client

    async def _get_robots(self, base_url: str) -> Optional[robotparser.RobotFileParser]:
        if not self.respect_robots:
            return None
        parsed = urlparse(base_url)
        netloc = parsed.netloc
        if netloc in self._robots_cache:
            return self._robots_cache[netloc]
        rp = robotparser.RobotFileParser()
        robots_url = f"{parsed.scheme}://{netloc}/robots.txt"
        try:
            client = await self._get_client()
            resp = await client.get(robots_url)
            if resp.status_code >= 400:
                rp.parse("")
            else:
                rp.parse(resp.text.splitlines())
        except Exception:
            rp.parse("")
        self._robots_cache[netloc] = rp
        return rp

    def _is_safe_url(self, url: str, base_netloc: str) -> bool:
        try:
            p = urlparse(url)
            if p.scheme not in ("http", "https"):
                return False
            host = p.hostname or ""
            host_l = host.lower()
            if host_l in {"localhost", "127.0.0.1"} or host_l.endswith(".local"):
                return False
            try:
                ip = ipaddress.ip_address(host_l)
                if ip.is_private or ip.is_loopback:
                    return False
            except ValueError:
                # not an IP literal
                pass
            # same-domain (allow subdomains)
            return host_l == base_netloc.lower() or host_l.endswith("." + base_netloc.lower())
        except Exception:
            return False

    def _allowed_by_robots(self, rp: Optional[robotparser.RobotFileParser], url: str) -> bool:
        if not self.respect_robots or rp is None:
            return True
        try:
            return rp.can_fetch(self.user_agent, url)
        except Exception:
            return False

    async def _sleep_with_delay(self, rp: Optional[robotparser.RobotFileParser]):
        base = self.delay_seconds
        try:
            if rp is not None:
                cd = rp.crawl_delay(self.user_agent)
                if cd:
                    base = max(base, float(cd))
        except Exception:
            pass
        await asyncio.sleep(base + random.uniform(0, 0.5))
