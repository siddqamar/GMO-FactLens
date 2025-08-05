import sqlite3
from typing import Dict, Any, List
import os
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database operations for article analysis results"""
    
    def __init__(self, db_path: str = 'articles.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database and create tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                summary TEXT,
                classification TEXT,
                fact_myth_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analysis_sessions table to track analysis runs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                articles_found INTEGER,
                facts_count INTEGER,
                myths_count INTEGER,
                unclear_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_article(self, article_data: Dict[str, Any]) -> bool:
        """Save a single article to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO articles (url, title, summary, classification, fact_myth_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                article_data['url'],
                article_data.get('title', ''),
                article_data.get('summary', ''),
                article_data.get('classification', ''),
                article_data.get('fact_myth_status', '')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving article to database: {e}")
            return False
    
    def save_articles_batch(self, articles: List[Dict[str, Any]]) -> int:
        """Save multiple articles to the database"""
        success_count = 0
        for article in articles:
            if self.save_article(article):
                success_count += 1
        return success_count
    
    def save_analysis_session(self, topic: str, articles: List[Dict[str, Any]]) -> int:
        """Save analysis session summary to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate statistics
            facts_count = sum(1 for a in articles if a.get('fact_myth_status') == 'Fact')
            myths_count = sum(1 for a in articles if a.get('fact_myth_status') == 'Myth')
            unclear_count = sum(1 for a in articles if a.get('fact_myth_status') == 'Unclear')
            
            cursor.execute('''
                INSERT INTO analysis_sessions (topic, articles_found, facts_count, myths_count, unclear_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (topic, len(articles), facts_count, myths_count, unclear_count))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            print(f"Error saving analysis session: {e}")
            return -1
    
    def get_recent_articles(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent articles from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT url, title, summary, classification, fact_myth_status, created_at
                FROM articles
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'url': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'classification': row[3],
                    'fact_myth_status': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return articles
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return []
    
    def get_analysis_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT topic, articles_found, facts_count, myths_count, unclear_count, created_at
                FROM analysis_sessions
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'topic': row[0],
                    'articles_found': row[1],
                    'facts_count': row[2],
                    'myths_count': row[3],
                    'unclear_count': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error retrieving analysis sessions: {e}")
            return []
    
    def get_articles_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get articles related to a specific topic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT url, title, summary, classification, fact_myth_status, created_at
                FROM articles
                WHERE url LIKE ? OR title LIKE ? OR summary LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{topic}%', f'%{topic}%', f'%{topic}%'))
            
            articles = []
            for row in cursor.fetchall():
                articles.append({
                    'url': row[0],
                    'title': row[1],
                    'summary': row[2],
                    'classification': row[3],
                    'fact_myth_status': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return articles
        except Exception as e:
            print(f"Error retrieving articles by topic: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_articles = cursor.fetchone()[0]
            
            # Articles by classification
            cursor.execute('''
                SELECT classification, COUNT(*) 
                FROM articles 
                GROUP BY classification
            ''')
            classification_stats = dict(cursor.fetchall())
            
            # Articles by fact/myth status
            cursor.execute('''
                SELECT fact_myth_status, COUNT(*) 
                FROM articles 
                GROUP BY fact_myth_status
            ''')
            status_stats = dict(cursor.fetchall())
            
            # Total analysis sessions
            cursor.execute('SELECT COUNT(*) FROM analysis_sessions')
            total_sessions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_articles': total_articles,
                'total_sessions': total_sessions,
                'classification_stats': classification_stats,
                'status_stats': status_stats
            }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {} 