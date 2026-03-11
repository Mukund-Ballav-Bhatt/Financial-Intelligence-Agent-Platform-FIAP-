import logging
import sqlite3
import os
from contextlib import contextmanager
from config import DB_PATH ,DB_TIMEOUT

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__ (self,path = DB_PATH):
        self.path = path
        logger.info(f"Database path is  : {path}")
    
    @contextmanager
    def connect_DB (self):
        conn = None
        try :
            conn = sqlite3.connect(self.path , timeout=DB_TIMEOUT)

            conn.row_factory = sqlite3.Row      #Making rowws in Dictionary
            conn.execute("PRAGMA foreign_keys = ON")

            logger.debug(f"database established")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database Connection Error : {e}")
            raise
        finally :
            if conn:
                conn.close()
                logger.debug("Connection closed")
    
    def test_connect(self):
        try:
            conn = sqlite3.connect(self.path, timeout=DB_TIMEOUT)
            conn.execute("SELECT 1")
            conn.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection Failed : {e}")
            return False
    
    def init_DB(self):
        try:
            curr_path = os.path.dirname(__file__)
            schema_path = os.path.join(curr_path , 'schema.sql')

            with open(schema_path , 'r') as f:
                schema = f.read()

            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema)            #since schema is a long string so executescript instead
                conn.commit()
                logger.info("Database initialised with all tables")
                return True
            
        except FileNotFoundError:
            logger.error(f"schema.sql not found at {schema_path}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error during initialization: {e}")
            return False

        except Exception as e:
            logger.error("Error in initialising database : {e}")
            return False
        
    def insert_stock_price(self, symbol, price, change=None, change_percent=None, volume=None, open=None, high=None, low=None, market_cap=None, pe_ratio=None):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO stock_prices(symbol, price, change, change_percent, volume, open, high, low, market_cap, pe_ratio)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,(symbol, price, change, change_percent, volume,
                  open, high, low, market_cap, pe_ratio))
                conn.commit()
                insert_id = cursor.lastrowid
                logger.info(f"Inserted stock price for {symbol}: ${price} (ID: {insert_id})")
                return insert_id
            
        except sqlite3.Error as e:
            logger.error(f"Failed to insert stock price for {symbol}: {e}")
            return None
    
    def get_latest_price(self,symbol):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                                SELECT * FROM stock_prices
                                WHERE symbol = ?
                                ORDER BY timestamp DESC         
                                LIMIT 1
                               """,(symbol,))               #Gives only latest record price
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    logger.warning(f"No stock price found for {symbol}")
                    return None
        except sqlite3.Error as e :
            logger.error(f"Failed to fetch stock price : {e}")
            return None

    def get_price_hist(self , symbol , limit = 30):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                                SELECT * FROM stock_prices
                                WHERE symbol = ? 
                                ORDER BY timestamp DESC 
                                LIMIT ?
                """, (symbol, limit))
            
                rows = cursor.fetchall()
                result = [dict(row) for row in rows] 
            return result
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get price history for {symbol}: {e}")
            return []
        
    def insert_article(self, symbol, headline, content=None, source=None, author=None, url=None, url_to_image=None, published_date=None, language='en'):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO news_articles 
                (symbol, headline, content, source, author, url, 
                 url_to_image, published_date, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, headline, content, source, author, url,url_to_image, published_date, language))
                conn.commit()
                insert_id = cursor.lastrowid
            logger.info(f"Inserted news article for {symbol}: {headline[:50]}... (ID: {insert_id})")
            return insert_id
        
        except sqlite3.IntegrityError as e:
            if 'UNIQUE' in str(e):
                logger.debug(f"Duplicate article skipped (URL already exists): {url}")
                return None
            else:
                logger.error(f"Integrity error inserting news for {symbol}: {e}")
                return None

        except sqlite3.Error() as e:
            logger.info(f"Failed inserting Article : {e}")
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
                        ORDER BY published_date DESC 
                        LIMIT ?
                    """, (symbol, f'-{days_back}', limit))
                else:
                    cursor.execute("""
                        SELECT * FROM news_articles 
                        WHERE symbol = ? 
                        ORDER BY published_date DESC 
                        LIMIT ?
                    """, (symbol, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get news for {symbol}: {e}")
            return []

    def get_article_by_url(self, url):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM news_articles 
                    WHERE url = ?
                """, (url,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except sqlite3.Error as e:
            logger.error(f"Failed to check article by URL: {e}")
            return None
        
    def insert_sentiment(self, news_id, sentiment, confidence, positive_score=0, negative_score=0, neutral_score=0,model_used='llama3.2', analysis_version='1.0'):
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
                
                inserted_id = cursor.lastrowid
                logger.info(f"Inserted sentiment for news_id {news_id}: {sentiment} ({confidence})")
                return inserted_id
                
        except sqlite3.IntegrityError as e:
            if 'FOREIGN KEY' in str(e):
                logger.error(f"Invalid news_id {news_id}: Article does not exist")
            else:
                logger.error(f"Integrity error inserting sentiment: {e}")
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
                    WHERE news_id = ?
                    ORDER BY analyzed_date DESC
                    LIMIT 1
                """, (news_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get sentiment for article {news_id}: {e}")
            return None
        
    def get_aggregate_sentiment(self, symbol, days_back=7):
    
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                
                # Get sentiment counts and average
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_articles,
                        SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
                        SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
                        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
                        SUM(CASE WHEN sentiment = 'mixed' THEN 1 ELSE 0 END) as mixed_count,
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
                    return {
                        'symbol': symbol,
                        'total_articles': 0,
                        'overall_sentiment': 'unknown',
                        'sentiment_score': 0,
                        'positive_pct': 0,
                        'neutral_pct': 0,
                        'negative_pct': 0,
                        'mixed_pct': 0,
                        'avg_confidence': 0,
                        'days_back': days_back
                    }
                
                # Calculate percentages
                total = row['total_articles']
                
                # Determine overall sentiment based on score
                score = row['sentiment_score'] or 0
                if score > 0.3:
                    overall = 'positive'
                elif score < -0.3:
                    overall = 'negative'
                elif -0.3 <= score <= 0.3 and score != 0:
                    overall = 'neutral'
                else:
                    overall = 'mixed' if row['mixed_count'] > 0 else 'neutral'
                
                result = {
                    'symbol': symbol,
                    'total_articles': total,
                    'overall_sentiment': overall,
                    'sentiment_score': round(score, 3),
                    'positive_pct': round((row['positive_count'] / total) * 100, 1),
                    'neutral_pct': round((row['neutral_count'] / total) * 100, 1),
                    'negative_pct': round((row['negative_count'] / total) * 100, 1),
                    'mixed_pct': round((row['mixed_count'] / total) * 100, 1),
                    'avg_confidence': round(row['avg_confidence'] or 0, 3),
                    'days_back': days_back
                }
                
                logger.info(f"Aggregate sentiment for {symbol}: {overall} ({total} articles)")
                return result
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get aggregate sentiment for {symbol}: {e}")
            return None

    def get_sentiment_trend(self, symbol, days=7):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        date(n.published_date) as day,
                        COUNT(*) as article_count,
                        AVG(CASE s.sentiment 
                            WHEN 'positive' THEN 1 
                            WHEN 'mixed' THEN 0.5
                            WHEN 'neutral' THEN 0 
                            WHEN 'negative' THEN -1 
                        END) as avg_sentiment
                    FROM news_articles n
                    JOIN sentiment_analysis s ON n.id = s.news_id
                    WHERE n.symbol = ? 
                    AND n.published_date > datetime('now', ? || ' days')
                    GROUP BY date(n.published_date)
                    ORDER BY day DESC
                """, (symbol, f'-{days}'))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get sentiment trend for {symbol}: {e}")
            return []


if __name__ == "__main__":
    db=DatabaseManager()
    #Testing Connection
    if db.test_connect():
        print(" Database connection successful!")
    else:
        print(" Database connection failed!")

    print("\n Initializing database tables...")
    if db.init_DB():                                #Initialising DB
        print(" Tables created successfully!")
    else:
        print(" Table creation failed!")

    print("\n Testing stock price insertion...")
    stock_id = db.insert_stock_price(
            symbol='AAPL',
            price=175.50,
            change=2.30,
            change_percent=1.33,
            volume=52400000,
            open=174.20,
            high=176.80,
            low=173.90,
            market_cap=2750000000000,
            pe_ratio=28.5
        )
        
    if stock_id:
        print(f"  Inserted AAPL stock price (ID: {stock_id})")
    else:
        print("  Failed to insert stock price")
        
        # Test 4: Get Latest Price
    print("\n Testing get_latest_price...")
    latest = db.get_latest_price('AAPL')
    if latest:
        print(f"  Latest AAPL price: ${latest['price']} at {latest['timestamp']}")
        print(f"     Change: {latest['change']} ({latest['change_percent']}%)")
    else:
        print("  Failed to get latest price")
        
        # Test 5: Get Price History
    print("\n Testing get_price_history...")
    history = db.get_price_hist('AAPL', limit=5)
    if history:
        print(f"  Retrieved {len(history)} historical records")
        for i, record in enumerate(history):
            print(f"     {i+1}. ${record['price']} at {record['timestamp']}")
    else:
        print("  Failed to get price history")

    print("\n Testing news article insertion...")
    
        # Test 6 : Inserting Artiles
    news_id = db.insert_article(
            symbol='AAPL',
            headline='Apple Announces New AI Features for iPhone',
            content='Apple today revealed groundbreaking AI features coming to iPhone...',
            source='TechCrunch',
            author='John Smith',
            url='https://techcrunch.com/apple-ai-2024',
            published_date='2024-03-11 10:30:00'
    )
        
    if news_id:
        print(f"  Inserted news article (ID: {news_id})")
    else:
        print("  Failed to insert news article (or duplicate)")
        
        # Insert another article (different URL)
    news_id2 = db.insert_article(
            symbol='AAPL',
            headline='Apple Stock Rises on AI Announcement',
            content='Apple shares jumped 2% following AI news...',
            source='Reuters',
            author='Jane Doe',
            url='https://reuters.com/apple-stock-2024',
            published_date='2024-03-11 11:45:00'
    )
        
    if news_id2:
        print(f"  Inserted second news article (ID: {news_id2})")
        
        # Test duplicate prevention (same URL)
    print("\n Testing duplicate prevention...")
    news_dup = db.insert_article(
            symbol='AAPL',
            headline='Duplicate Test',
            content='This should be skipped',
            url='https://techcrunch.com/apple-ai-2024'  # Same URL as first
    )
        
    if news_dup is None:
        print("  Duplicate correctly rejected (returned None)")
    else:
        print("  Duplicate was inserted (should not happen)")
        
    # Test get_news_for_symbol
    print("\n Testing get_news_for_symbol...")
    articles = db.get_news_for_symbol('AAPL', limit=5)
    
    if articles:
        print(f"  Retrieved {len(articles)} articles for AAPL:")
        for i, article in enumerate(articles):
            print(f"     {i+1}. {article['headline'][:60]}...")
            print(f"        Source: {article['source']}, Date: {article['published_date']}")
    else:
        print("  Failed to get news articles")
    
    # Test with days_back filter
    print("\n Testing get_news_for_symbol with days_back=7...")
    recent = db.get_news_for_symbol('AAPL', days_back=7, limit=5)
    print(f"  Found {len(recent)} articles from last 7 days")
    print("\n" + "="*50)
    print(" TESTING SENTIMENT OPERATIONS")
    print("="*50)
    
    # Get the news IDs we just inserted
    print("\nGetting news articles for sentiment analysis...")
    articles = db.get_news_for_symbol('AAPL', limit=2)
    
    if len(articles) >= 2:
        # Insert sentiment for first article
        print("\n Inserting sentiment for first article...")
        sent1_id = db.insert_sentiment(
            news_id=articles[0]['id'],
            sentiment='positive',
            confidence=0.92,
            positive_score=0.85,
            negative_score=0.08,
            neutral_score=0.07
        )
        
        if sent1_id:
            print(f"  Inserted positive sentiment (ID: {sent1_id})")
        else:
            print("  Failed to insert sentiment")
        
        # Insert sentiment for second article
        print("\n Inserting sentiment for second article...")
        sent2_id = db.insert_sentiment(
            news_id=articles[1]['id'],
            sentiment='positive',
            confidence=0.78,
            positive_score=0.70,
            negative_score=0.15,
            neutral_score=0.15
        )
        
        if sent2_id:
            print(f"  Inserted positive sentiment (ID: {sent2_id})")
        
        # Test get_sentiment_for_article
        print("\n Testing get_sentiment_for_article...")
        sentiment = db.get_sentiment_for_article(articles[0]['id'])
        if sentiment:
            print(f"   Retrieved sentiment for article {articles[0]['id']}:")
            print(f"     Sentiment: {sentiment['sentiment']}")
            print(f"     Confidence: {sentiment['confidence']}")
        else:
            print("   Failed to get sentiment")
        
        # Test get_aggregate_sentiment
        print("\n Testing get_aggregate_sentiment...")
        agg = db.get_aggregate_sentiment('AAPL', days_back=7)
        if agg:
            print(f"   Aggregate sentiment for AAPL:")
            print(f"     Overall: {agg['overall_sentiment']}")
            print(f"     Score: {agg['sentiment_score']}")
            print(f"     Articles: {agg['total_articles']}")
            print(f"     Positive: {agg['positive_pct']}%")
            print(f"     Neutral: {agg['neutral_pct']}%")
            print(f"     Negative: {agg['negative_pct']}%")
        else:
            print("   Failed to get aggregate sentiment")
        
        # Test foreign key constraint
        print("\n Testing foreign key constraint (invalid news_id)...")
        invalid = db.insert_sentiment(
            news_id=99999,  # This ID doesn't exist
            sentiment='positive',
            confidence=0.95
        )
        
        if invalid is None:
            print("  Foreign key constraint working (rejected invalid news_id)")
        else:
            print("  Foreign key constraint failed")
            
    else:
        print("  Not enough articles found for sentiment testing")