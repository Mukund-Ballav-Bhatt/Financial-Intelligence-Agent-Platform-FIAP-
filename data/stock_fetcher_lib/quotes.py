import logging
from .base import BaseStockFetcher
from datetime import datetime

logger = logging.getLogger(__name__)

class QuoteOperations(BaseStockFetcher):    
    def fetch_stock(self, symbol):
        try:
            logger.info(f"Fetching data for {symbol}...")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                logger.error(f"Could not create ticker for {symbol}")
                return None
            
            info = ticker.info
            current_price = self._extract_price(info, ticker)
            
            if current_price is None:
                logger.error(f"Could not extract price for {symbol}")
                return None
            
            stock_data = {
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(info.get('regularMarketChange', 0), 2),
                'change_percent': round(info.get('regularMarketChangePercent', 0), 2),
                'volume': info.get('volume', info.get('regularMarketVolume', 0)),
                'open': round(info.get('regularMarketOpen', 0), 2) if info.get('regularMarketOpen') else None,
                'high': round(info.get('regularMarketDayHigh', 0), 2) if info.get('regularMarketDayHigh') else None,
                'low': round(info.get('regularMarketDayLow', 0), 2) if info.get('regularMarketDayLow') else None,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': round(info.get('trailingPE', info.get('forwardPE', 0)), 2) if info.get('trailingPE') else None,
                'timestamp': datetime.now().isoformat()
            }
            
            stock_data_for_db = stock_data.copy()
            stock_data_for_db.pop('timestamp', None)  # Remove timestamp field
            db_id = self.db.insert_stock_price(**stock_data_for_db)
            
            if db_id:
                logger.info(f"✅ Successfully fetched and stored {symbol}: ₹${current_price}")
                stock_data['id'] = db_id
                return stock_data
            else:
                logger.error(f"Failed to store {symbol} in database")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_multiple_stocks(self, symbols, delay=1):
        results = {}
        successful = 0
        failed = 0
        
        logger.info(f"Fetching data for {len(symbols)} stocks: {symbols}")
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Processing {i+1}/{len(symbols)}: {symbol}")
            
            data = self.fetch_stock(symbol)
            if data:
                results[symbol] = data
                successful += 1
            else:
                failed += 1
            
            self._delay_if_needed(i, len(symbols), delay)
        
        logger.info(f"✅ Completed: {successful} successful, {failed} failed")
        return results
    
    def get_quote_summary(self, symbol):
        data = self.fetch_stock(symbol)
        if not data:
            return None
        
        return {
            'symbol': data['symbol'],
            'price': data['price'],
            'change': data['change'],
            'change_percent': data['change_percent'],
            'volume': data['volume'],
            'timestamp': data['timestamp']
        }
    
    def compare_stocks(self, symbols):
        data = self.fetch_multiple_stocks(symbols, delay=0.5)
        comparison = {
            'symbols': symbols,
            'timestamp': datetime.now().isoformat(),
            'stocks': data,
            'summary': {
                'highest_price': None,
                'lowest_price': None,
                'biggest_gainer': None,
                'biggest_loser': None
            }
        }
        
        if data:
            prices = [(sym, d['price']) for sym, d in data.items()]
            if prices:
                highest = max(prices, key=lambda x: x[1])
                lowest = min(prices, key=lambda x: x[1])
                comparison['summary']['highest_price'] = {'symbol': highest[0], 'price': highest[1]}
                comparison['summary']['lowest_price'] = {'symbol': lowest[0], 'price': lowest[1]}
            
            changes = [(sym, d['change_percent']) for sym, d in data.items()]
            if changes:
                gainer = max(changes, key=lambda x: x[1])
                loser = min(changes, key=lambda x: x[1])
                comparison['summary']['biggest_gainer'] = {'symbol': gainer[0], 'change': gainer[1]}
                comparison['summary']['biggest_loser'] = {'symbol': loser[0], 'change': loser[1]}
        
        return comparison