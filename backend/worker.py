import asyncio
import os
from celery import Celery
from crawler import WebCrawler
from database import Database

# Initialize Celery
celery_app = Celery(
    'serverai_worker',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379')
)

# Initialize components
crawler = WebCrawler()
db = Database()

@celery_app.task
def crawl_site_task(site_url: str, task_id: str):
    """Celery task for crawling a single site"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(db.init_db())
        loop.run_until_complete(crawler._crawl_site(site_url))
        return f"Successfully crawled {site_url}"
    except Exception as e:
        return f"Error crawling {site_url}: {str(e)}"
    finally:
        loop.close()

if __name__ == "__main__":
    # Start the worker
    celery_app.start()