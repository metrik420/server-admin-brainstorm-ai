import asyncpg
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None

    async def init_db(self):
        """Initialize database connection and tables"""
        self.pool = await asyncpg.create_pool(self.database_url)
        
        async with self.pool.acquire() as conn:
            # Create tables
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_tasks (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress FLOAT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_stats (
                    id SERIAL PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def get_statistics(self):
        """Get dashboard statistics"""
        async with self.pool.acquire() as conn:
            total_articles = await conn.fetchval("SELECT COUNT(*) FROM articles")
            topics_covered = await conn.fetchval("SELECT COUNT(DISTINCT topic) FROM articles")
            
            # Active crawlers (tasks in running state)
            active_crawlers = await conn.fetchval(
                "SELECT COUNT(*) FROM crawl_tasks WHERE status = 'running'"
            )
            
            # Last update
            last_update = await conn.fetchval(
                "SELECT MAX(created_at) FROM articles"
            )
            
            return {
                "total_articles": total_articles or 0,
                "active_crawlers": active_crawlers or 0,
                "topics_covered": topics_covered or 0,
                "last_update": last_update.isoformat() if last_update else "Never"
            }

    async def get_topic_stats(self):
        """Get statistics by topic"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT topic, COUNT(*) as count, MAX(created_at) as last_update
                FROM articles 
                GROUP BY topic 
                ORDER BY count DESC
            """)
            
            return [
                {
                    "name": row["topic"],
                    "count": row["count"],
                    "last_update": row["last_update"].isoformat() if row["last_update"] else None
                }
                for row in rows
            ]

    async def save_article(self, url: str, content: str, topic: str):
        """Save an article to the database"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO articles (url, content, topic) 
                VALUES ($1, $2, $3)
                ON CONFLICT (url) DO UPDATE SET
                    content = EXCLUDED.content,
                    topic = EXCLUDED.topic,
                    updated_at = NOW()
            """, url, content, topic)

    async def create_crawl_task(self, task_id: str, status: str):
        """Create a new crawl task"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO crawl_tasks (id, status) VALUES ($1, $2)
            """, task_id, status)

    async def update_crawl_task(self, task_id: str, status: str):
        """Update crawl task status"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE crawl_tasks SET status = $2, updated_at = NOW() 
                WHERE id = $1
            """, task_id, status)

    async def update_crawl_progress(self, task_id: str, progress: float):
        """Update crawl progress"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE crawl_tasks SET progress = $2, updated_at = NOW() 
                WHERE id = $1
            """, task_id, progress)

    async def get_crawl_progress(self, task_id: str):
        """Get crawl progress"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT progress FROM crawl_tasks WHERE id = $1", task_id
            ) or 0

    async def get_articles_by_topic(self, topic: str):
        """Get articles for a specific topic"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT url, title, created_at FROM articles 
                WHERE topic = $1 ORDER BY created_at DESC LIMIT 100
            """, topic)
            
            return [
                {
                    "url": row["url"],
                    "title": row["title"] or "Untitled",
                    "created_at": row["created_at"].isoformat()
                }
                for row in rows
            ]

    async def search_articles(self, query: str):
        """Search articles by content"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT url, title, topic, created_at FROM articles 
                WHERE content ILIKE $1 OR title ILIKE $1
                ORDER BY created_at DESC LIMIT 50
            """, f"%{query}%")
            
            return [
                {
                    "url": row["url"],
                    "title": row["title"] or "Untitled",
                    "topic": row["topic"],
                    "created_at": row["created_at"].isoformat()
                }
                for row in rows
            ]

    async def get_sites_crawled(self):
        """Get number of unique sites crawled"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT COUNT(DISTINCT SPLIT_PART(url, '/', 3)) FROM articles
            """) or 0

    async def get_total_articles(self):
        """Get total number of articles"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM articles") or 0

    async def get_last_update(self):
        """Get last update timestamp"""
        async with self.pool.acquire() as conn:
            last_update = await conn.fetchval("SELECT MAX(created_at) FROM articles")
            if last_update:
                return last_update.isoformat()
            return "Never"