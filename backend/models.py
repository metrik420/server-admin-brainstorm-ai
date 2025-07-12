from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CrawlTask(BaseModel):
    id: str
    status: str
    progress: float = 0.0
    created_at: datetime
    updated_at: datetime

class CrawlStatus(BaseModel):
    is_running: bool
    task_id: Optional[str] = None
    progress: float = 0.0
    sites_crawled: int = 0
    pages_found: int = 0
    last_update: str = "Never"

class Article(BaseModel):
    url: str
    title: Optional[str] = None
    content: str
    topic: str
    created_at: datetime

class TopicStats(BaseModel):
    name: str
    count: int
    last_update: Optional[str] = None

class SearchResult(BaseModel):
    url: str
    title: str
    topic: str
    created_at: str