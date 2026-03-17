import logging
import sqlite3
from .base import DatabaseBase

logger = logging.getLogger(__name__)

class NewsOperations(DatabaseBase):
    
    def insert_article(self, symbol, headline, content=None, source=None, 
                       author=None, url=None, url_to_image=None, 
                       published_date=None, language='en'):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO news_articles 
                    (symbol, headline, content, source, author, url, 
                     url_to_image, published_date, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, headline, content, source, author, url,
                      url_to_image, published_date, language))
                conn.commit()
                insert_id = cursor.lastrowid
                logger.info(f"Inserted news article for {symbol}: {headline[:30]}... (ID: {insert_id})")
                return insert_id
        except sqlite3.IntegrityError as e:
            if 'UNIQUE' in str(e):
                logger.debug(f"Duplicate article skipped: {url}")
                return None
            logger.error(f"Integrity error: {e}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to insert article: {e}")
            return None
    
    def get_news_for_symbol(self, symbol, limit=10, days_back=None):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                if days_back:
                    cursor.execute("""
                        SELECT * FROM news_articles 
                        WHERE symbol = ? 
                        AND published_date > datetime('now', ? || ' days')
                        ORDER BY published_date DESC LIMIT ?
                    """, (symbol, f'-{days_back}', limit))
                else:
                    cursor.execute("""
                        SELECT * FROM news_articles 
                        WHERE symbol = ? 
                        ORDER BY published_date DESC LIMIT ?
                    """, (symbol, limit))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get news for {symbol}: {e}")
            return []
    
    def get_article_by_url(self, url):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM news_articles WHERE url = ?", (url,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to check article by URL: {e}")
            return None