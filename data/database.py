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