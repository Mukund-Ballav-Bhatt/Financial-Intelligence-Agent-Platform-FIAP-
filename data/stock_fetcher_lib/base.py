import logging
import yfinance as yf
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database_lib import DatabaseManager

logger = logging.getLogger(__name__)

class BaseStockFetcher:
    
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        logger.info(f"BaseStockFetcher initialized with database: {self.db.path}")
    
    def _get_ticker(self, symbol):                                  #Methods with '_' are protected
        try:
            logger.debug(f"Creating ticker for {symbol}")
            return yf.Ticker(symbol)
        except Exception as e:
            logger.error(f"Error creating ticker for {symbol}: {e}")
            return None
    
    def _extract_price(self, info, ticker):
        price = info.get('regularMarketPrice', info.get('currentPrice', info.get('ask', info.get('bid', None))))
        
        if price is None:
            logger.debug(f"No price in info, trying history for {info.get('symbol', 'unknown')}")
            try:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            except Exception as e:
                logger.error(f"Error getting history: {e}")
        
        return price
    
    def _delay_if_needed(self, current_index, total_items, delay=1):
        if current_index < total_items - 1 and delay > 0:
            logger.debug(f"Waiting {delay} seconds before next request...")
            time.sleep(delay)
    
    def test_connection(self):
        try:
            ticker = self._get_ticker('AAPL')
            if ticker:
                info = ticker.info
                if info.get('regularMarketPrice'):
                    logger.info("yfinance connection successful")
                    return True
            logger.warning(" yfinance connection test returned no data")
            return False
        except Exception as e:
            logger.error(f" yfinance connection failed: {e}")
            return False