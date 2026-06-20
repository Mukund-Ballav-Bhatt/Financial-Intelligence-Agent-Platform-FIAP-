import logging
from datetime import datetime
from .base import BaseStockFetcher
from .quotes import QuoteOperations
from .historical import HistoricalOperations
from .company import CompanyOperations
from .validator import ValidatorOperations

logger = logging.getLogger(__name__)

class StockFetcher(QuoteOperations,HistoricalOperations,CompanyOperations,ValidatorOperations,BaseStockFetcher): 
    def __init__(self, db_manager=None):
        super().__init__(db_manager)
        logger.info(" StockFetcher fully initialized with ALL operations:")
        logger.info("    Quote operations (current prices)")
        logger.info("    Historical operations (trends, moving averages)")
        logger.info("    Company operations (info, financials, analyst ratings)")
        logger.info("    Validator operations (symbol checking, suggestions)")
    
    def get_complete_profile(self, symbol):
        logger.info(f" Building complete profile for {symbol}...")
        
        if not self.validate_symbol(symbol):
            logger.warning(f"Symbol {symbol} may be invalid")
            suggestion = self.suggest_correction(symbol)
            if suggestion['suggestions']:
                logger.info(f"Did you mean: {suggestion['suggestions'][0]['suggestion']}")
        
        profile = {
            'symbol': symbol.upper(),
            'timestamp': datetime.now().isoformat(),
            'validation': {
                'is_valid': self.validate_symbol(symbol),
                'exchange': self.get_exchange_info(symbol)
            }
        }
        
        logger.info("   Fetching current quote...")
        profile['quote'] = self.get_quote_summary(symbol)
        
        logger.info("   Analyzing trends...")
        profile['trend_1month'] = self.get_price_trend(symbol, days=30)
        profile['trend_3month'] = self.get_price_trend(symbol, days=90)
        profile['moving_averages'] = self.get_multiple_moving_averages(symbol)
        
        logger.info("   Fetching company details...")
        profile['company_info'] = self.get_company_summary(symbol)
        profile['financials'] = self.get_key_financials(symbol)
        
        logger.info("   Checking analyst ratings...")
        profile['analyst_ratings'] = self.get_analyst_recommendations(symbol)
        
        logger.info("   Checking insider transactions...")
        profile['insider_activity'] = self.get_insider_transactions(symbol)
        
        profile['data_completeness'] = self._calculate_completeness(profile)
        
        logger.info(f" Complete profile built for {symbol}")
        return profile
    
    def _calculate_completeness(self, profile):
        sections = ['quote', 'trend_1month', 'company_info', 'financials', 'analyst_ratings']
        total = len(sections)
        present = 0
        
        for section in sections:
            if profile.get(section) is not None:
                present += 1
        
        return {
            'sections_present': present,
            'total_sections': total,
            'percentage': round((present / total) * 100, 1),
            'summary': f"{present}/{total} sections available"
        }
    
    def quick_scan(self, symbols):
        logger.info(f" Quick scanning {len(symbols)} stocks...")
        
        scan_results = {
            'timestamp': datetime.now().isoformat(),
            'symbols_scanned': len(symbols),
            'results': {},
            'summary': {}
        }
        
        for symbol in symbols:
            quote = self.get_quote_summary(symbol)
            if quote:
                scan_results['results'][symbol] = {
                    'price': quote['price'],
                    'change': quote['change_percent'],
                    'volume': quote['volume']
                }
        
        if scan_results['results']:
            prices = [r['price'] for r in scan_results['results'].values()]
            changes = [r['change'] for r in scan_results['results'].values()]
            
            scan_results['summary'] = {
                'stocks_found': len(scan_results['results']),
                'avg_price': round(sum(prices) / len(prices), 2),
                'avg_change': round(sum(changes) / len(changes), 2),
                'highest_change': max(changes) if changes else 0,
                'lowest_change': min(changes) if changes else 0,
                'most_volatile': max(changes, key=abs) if changes else 0
            }
        
        logger.info(f" Quick scan complete: found {scan_results['summary'].get('stocks_found', 0)} stocks")
        return scan_results
    
    def search_by_name(self, company_name):
        """
        Search for stocks by company name (simplified version).
        Note: This is a basic implementation - in production, use a proper symbols database.
        
        Args:
            company_name (str): Company name to search for
        
        Returns:
            list: Possible matching symbols
        """
        name_to_symbol = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
            'tata': 'TCS.NS, TATAMOTORS.NS',
            'reliance': 'RELIANCE.NS',
            'infosys': 'INFY.NS',
            'hdfc': 'HDFCBANK.NS',
            'icici': 'ICICIBANK.NS'
        }
        
        search_term = company_name.lower().strip()
        results = []
        
        for name, symbol in name_to_symbol.items():
            if name in search_term or search_term in name:
                results.append({
                    'company': name.title(),
                    'symbol': symbol,
                    'match_type': 'partial' if name != search_term else 'exact'
                })
        
        return results
    
    def market_summary(self, symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'RELIANCE.NS', 'TCS.NS']):
        logger.info("📈 Generating market summary...")
        
        data = self.fetch_multiple_stocks(symbols, delay=0.3)
        
        if not data:
            return None
        
        changes = [d['change_percent'] for d in data.values()]
        prices = [d['price'] for d in data.values()]
        
        up_stocks = len([c for c in changes if c > 0])
        down_stocks = len([c for c in changes if c < 0])
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'stocks_tracked': len(data),
            'market_mood': 'BULLISH' if up_stocks > down_stocks else 'BEARISH' if down_stocks > up_stocks else 'NEUTRAL',
            'advancers': up_stocks,
            'decliners': down_stocks,
            'avg_change': round(sum(changes) / len(changes), 2),
            'avg_price': round(sum(prices) / len(prices), 2),
            'top_gainer': max(data.items(), key=lambda x: x[1]['change_percent'])[0] if data else None,
            'top_loser': min(data.items(), key=lambda x: x[1]['change_percent'])[0] if data else None,
            'details': data
        }
        
        return summary