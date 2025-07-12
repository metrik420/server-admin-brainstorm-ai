-- Initialize database with required tables and indexes

-- Articles table for storing crawled content
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    topic TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crawl tasks for tracking crawler status
CREATE TABLE IF NOT EXISTS crawl_tasks (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    progress FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stats table for caching metrics
CREATE TABLE IF NOT EXISTS crawl_stats (
    id SERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_topic ON articles(topic);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_crawl_tasks_status ON crawl_tasks(status);

-- Create full-text search index for content
CREATE INDEX IF NOT EXISTS idx_articles_content_search ON articles USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_articles_title_search ON articles USING gin(to_tsvector('english', title));

-- Insert some initial data for demo
INSERT INTO articles (url, title, content, topic) VALUES 
('https://example.com/linux-basics', 'Linux Basics Guide', 'This is a comprehensive guide to Linux system administration...', 'linux'),
('https://example.com/mysql-setup', 'MySQL Database Setup', 'Learn how to set up and configure MySQL database server...', 'mysql'),
('https://example.com/apache-config', 'Apache Configuration', 'Complete guide to Apache web server configuration...', 'apache')
ON CONFLICT (url) DO NOTHING;