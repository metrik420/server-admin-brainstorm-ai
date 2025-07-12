import asyncio
import requests
from bs4 import BeautifulSoup
import trafilatura
from langdetect import detect
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import aiofiles
from database import Database

class WebCrawler:
    def __init__(self):
        self.db = Database()
        self.storage_path = os.getenv("STORAGE_PATH", "/app/storage")
        self.is_running = False
        self.current_task_id = None
        
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
        """Execute the crawling process"""
        try:
            await self.db.update_crawl_task(task_id, "running")
            
            for i, target in enumerate(self.crawl_targets):
                if not self.is_running:
                    break
                    
                print(f"Crawling {target}...")
                await self._crawl_site(target)
                
                # Update progress
                progress = ((i + 1) / len(self.crawl_targets)) * 100
                await self.db.update_crawl_progress(task_id, progress)
                
                # Small delay between sites
                await asyncio.sleep(2)
            
            await self.db.update_crawl_task(task_id, "completed")
            
        except Exception as e:
            print(f"Crawl error: {e}")
            await self.db.update_crawl_task(task_id, "failed")
        finally:
            self.is_running = False
            self.current_task_id = None

    async def _crawl_site(self, base_url: str):
        """Crawl a specific site"""
        try:
            # Simple implementation - in production, use more sophisticated crawling
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    if href.startswith('http'):
                        links.append(href)
                
                # Process first 10 links (limit for demo)
                for link in links[:10]:
                    if not self.is_running:
                        break
                    await self._process_page(link)
                    
        except Exception as e:
            print(f"Error crawling {base_url}: {e}")

    async def _process_page(self, url: str):
        """Process and classify a single page"""
        try:
            # Extract clean text
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return
                
            text = trafilatura.extract(downloaded)
            if not text or len(text) < 500:  # Skip short pages
                return
            
            # Detect language
            try:
                lang = detect(text)
                if lang != 'en':
                    return  # Skip non-English content
            except:
                return
            
            # Classify topic
            topic = self._classify_topic(text, url)
            if not topic:
                topic = "general"
            
            # Save to database
            await self.db.save_article(url, text, topic)
            
            # Save to file
            await self._save_to_file(url, text, topic)
            
        except Exception as e:
            print(f"Error processing {url}: {e}")

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