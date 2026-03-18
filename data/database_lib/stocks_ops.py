import logging
import sqlite3
from .base import DatabaseBase

logger = logging.getLogger(__name__)

class StockOperations(DatabaseBase):
    
    def insert_stock_price(self, symbol, price, change=None, change_percent=None, 
                           volume=None, open=None, high=None, low=None, 
                           market_cap=None, pe_ratio=None,timestamp=None):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO stock_prices 
                    (symbol, price, change, change_percent, volume, 
                     open, high, low, market_cap, pe_ratio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, price, change, change_percent, volume,
                      open, high, low, market_cap, pe_ratio))
                conn.commit()
                insert_id = cursor.lastrowid
                logger.info(f"Inserted stock price for {symbol}: ${price} (ID: {insert_id})")
                return insert_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert stock price for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM stock_prices
                    WHERE symbol = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (symbol,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch stock price: {e}")
            return None
    
    def get_price_hist(self, symbol, limit=30):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM stock_prices
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC LIMIT ?
                """, (symbol, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to get price history for {symbol}: {e}")
            return []
    
    def init_stock_table(self):
        """Initialize just stock table (if needed separately)"""
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        change REAL,
                        change_percent REAL,
                        volume INTEGER,
                        open REAL,
                        high REAL,
                        low REAL,
                        market_cap REAL,
                        pe_ratio REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        currency TEXT DEFAULT 'USD',
                        data_source TEXT DEFAULT 'yfinance'
                    )
                """)
                conn.commit()
                logger.info("Stock prices table initialized")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to init stock table: {e}")
            return False