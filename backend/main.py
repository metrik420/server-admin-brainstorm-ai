from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import aiofiles
import os
from datetime import datetime
from typing import List, Dict
import json
from crawler import WebCrawler
from database import Database
from models import CrawlTask, CrawlStatus, TopicStats

app = FastAPI(title="ServerAI Knowledge Engine API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
crawler = WebCrawler()

@app.on_event("startup")
async def startup_event():
    await db.init_db()

@app.get("/")
async def root():
    return {"message": "ServerAI Knowledge Engine API", "status": "running"}

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    stats = await db.get_statistics()
    return {
        "total_articles": stats.get("total_articles", 0),
        "active_crawlers": stats.get("active_crawlers", 0),
        "topics_covered": stats.get("topics_covered", 0),
        "last_update": stats.get("last_update", "Never")
    }

@app.get("/api/topics")
async def get_topics():
    """Get topic statistics"""
    topics = await db.get_topic_stats()
    return topics

@app.get("/api/crawler/status")
async def get_crawler_status():
    """Get current crawler status"""
    status = await crawler.get_status()
    return status

@app.post("/api/crawler/start")
async def start_crawler(background_tasks: BackgroundTasks):
    """Start the web crawler"""
    task_id = await crawler.start_crawl()
    background_tasks.add_task(crawler.run_crawl, task_id)
    return {"message": "Crawler started", "task_id": task_id}

@app.post("/api/crawler/stop")
async def stop_crawler():
    """Stop the web crawler"""
    await crawler.stop_crawl()
    return {"message": "Crawler stopped"}

@app.get("/api/articles/{topic}")
async def get_articles_by_topic(topic: str):
    """Get articles for a specific topic"""
    articles = await db.get_articles_by_topic(topic)
    return articles

@app.get("/api/search")
async def search_articles(q: str):
    """Search articles by query"""
    results = await db.search_articles(q)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)