import logging
import sqlite3
from .base import DatabaseBase

logger = logging.getLogger(__name__)

class SentimentOperations(DatabaseBase):    
    def insert_sentiment(self, news_id, sentiment, confidence, 
                        positive_score=0, negative_score=0, neutral_score=0,
                        model_used='llama3.2', analysis_version='1.0'):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sentiment_analysis 
                    (news_id, sentiment, confidence, positive_score, 
                     negative_score, neutral_score, model_used, analysis_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (news_id, sentiment, confidence, positive_score,
                      negative_score, neutral_score, model_used, analysis_version))
                conn.commit()
                insert_id = cursor.lastrowid
                logger.info(f"Inserted sentiment for news_id {news_id}: {sentiment}")
                return insert_id
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY' in str(e):
                logger.error(f"Invalid news_id {news_id}")
            else:
                logger.error(f"Integrity error: {e}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to insert sentiment: {e}")
            return None
    
    def get_sentiment_for_article(self, news_id):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM sentiment_analysis 
                    WHERE news_id = ? ORDER BY analyzed_date DESC LIMIT 1
                """, (news_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get sentiment: {e}")
            return None
    
    def get_aggregate_sentiment(self, symbol, days_back=7):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_articles,
                        SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as pos_count,
                        SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neu_count,
                        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as neg_count,
                        AVG(confidence) as avg_confidence,
                        AVG(CASE sentiment 
                            WHEN 'positive' THEN 1 
                            WHEN 'mixed' THEN 0.5
                            WHEN 'neutral' THEN 0 
                            WHEN 'negative' THEN -1 
                        END) as sentiment_score
                    FROM news_articles n
                    JOIN sentiment_analysis s ON n.id = s.news_id
                    WHERE n.symbol = ? 
                    AND n.published_date > datetime('now', ? || ' days')
                """, (symbol, f'-{days_back}'))
                
                row = cursor.fetchone()
                if not row or row['total_articles'] == 0:
                    return {'symbol': symbol, 'total_articles': 0, 'overall_sentiment': 'unknown'}
                
                total = row['total_articles']
                score = row['sentiment_score'] or 0
                
                if score > 0.3:
                    overall = 'positive'
                elif score < -0.3:
                    overall = 'negative'
                else:
                    overall = 'neutral'
                
                return {
                    'symbol': symbol,
                    'total_articles': total,
                    'overall_sentiment': overall,
                    'sentiment_score': round(score, 3),
                    'positive_pct': round((row['pos_count']/total)*100, 1),
                    'neutral_pct': round((row['neu_count']/total)*100, 1),
                    'negative_pct': round((row['neg_count']/total)*100, 1),
                    'avg_confidence': round(row['avg_confidence'] or 0, 3)
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to get aggregate sentiment: {e}")
            return None