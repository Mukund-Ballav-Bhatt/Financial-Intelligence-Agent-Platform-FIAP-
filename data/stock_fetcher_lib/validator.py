import logging
from .base import BaseStockFetcher

logger = logging.getLogger(__name__)

class ValidatorOperations(BaseStockFetcher):    
    def validate_symbol(self, symbol):
        try:
            logger.info(f"Validating symbol: {symbol}")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                logger.warning(f"✗ Could not create ticker for {symbol}")
                return False
            
            info = ticker.info
            
            if info.get('longName') or info.get('shortName') or info.get('regularMarketPrice'):
                logger.info(f"✓ {symbol} is VALID - {info.get('longName', info.get('shortName', 'Unknown'))}")
                return True
            else:
                hist = ticker.history(period="1d")
                if not hist.empty:
                    logger.info(f"✓ {symbol} is VALID (based on history data)")
                    return True
                else:
                    logger.warning(f"✗ {symbol} appears to be INVALID (no data found)")
                    return False
                
        except Exception as e:
            logger.error(f"Error validating {symbol}: {e}")
            return False
    
    def validate_multiple_symbols(self, symbols):
        logger.info(f"Validating {len(symbols)} symbols: {symbols}")
        
        results = {
            'valid': [],
            'invalid': [],
            'total': len(symbols),
            'valid_count': 0,
            'invalid_count': 0,
            'details': {}
        }
        
        for symbol in symbols:
            is_valid = self.validate_symbol(symbol)
            results['details'][symbol] = is_valid
            
            if is_valid:
                results['valid'].append(symbol)
                results['valid_count'] += 1
            else:
                results['invalid'].append(symbol)
                results['invalid_count'] += 1
        
        logger.info(f" Validation complete: {results['valid_count']} valid, {results['invalid_count']} invalid")
        return results
    
    def suggest_correction(self, symbol):
        original = symbol.upper().strip()
        suggestions = []
        
        common_mistakes = {
            'APPL': 'AAPL (Apple Inc.)',
            'GOGL': 'GOOGL (Google/Alphabet)',
            'GOOG': 'GOOGL (Google Class A) or GOOG (Google Class C)',
            'MSTF': 'MSFT (Microsoft)',
            'AMZ': 'AMZN (Amazon)',
            'AMAZN': 'AMZN (Amazon)',
            'TSL': 'TSLA (Tesla)',
            'TESLA': 'TSLA (Tesla)',
            'FACEBOOK': 'META (Meta/Facebook)',
            'FB': 'META (Meta/Facebook)',
            'NVD': 'NVDA (NVIDIA)',
            'NIVIDA': 'NVDA (NVIDIA)',
            'INFT': 'INFY (Infosys)',
            'INFOSYS': 'INFY (Infosys)',
            'TATAMOTORS': 'TATAMOTORS.NS (Tata Motors - India)',
            'RELIANCE': 'RELIANCE.NS (Reliance Industries - India)',
            'TCS': 'TCS.NS (Tata Consultancy Services - India)',
            'HDFC': 'HDFCBANK.NS (HDFC Bank - India)',
            'ICICI': 'ICICIBANK.NS (ICICI Bank - India)',
            'WIPRO': 'WIPRO.NS (Wipro - India)'
        }
        
        if original in common_mistakes:
            suggestions.append({
                'original': original,
                'suggestion': common_mistakes[original],
                'confidence': 'HIGH',
                'reason': 'Common typo correction'
            })
        
        if not '.' in original and self._is_likely_indian_stock(original):
            suggestions.append({
                'original': original,
                'suggestion': f"{original}.NS (India - NSE)",
                'confidence': 'MEDIUM',
                'reason': 'Indian stocks often need .NS suffix'
            })
        
        if original.startswith('$'):
            suggestions.append({
                'original': original,
                'suggestion': original[1:],
                'confidence': 'LOW',
                'reason': 'Remove $ prefix'
            })
        
        if not suggestions:
            similar = self._find_similar_symbols(original)
            if similar:
                suggestions.extend(similar)
        
        result = {
            'original_symbol': original,
            'is_valid': self.validate_symbol(original),
            'suggestions': suggestions,
            'suggestion_count': len(suggestions)
        }
        
        if result['is_valid']:
            result['message'] = f"✓ {original} is already valid!"
        elif suggestions:
            result['message'] = f"ℹ Found {len(suggestions)} suggestion(s)"
        else:
            result['message'] = f"✗ No suggestions found for {original}"
        
        return result
    
    def _is_likely_indian_stock(self, symbol):
        indian_stocks = [
            'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY',
            'WIPRO', 'TATAMOTORS', 'TATASTEEL', 'SUNPHARMA',
            'BHARTIARTL', 'ITC', 'SBIN', 'KOTAKBANK', 'BAJFINANCE',
            'HINDUNILVR', 'ASIANPAINT', 'MARUTI', 'TECHM', 'NTPC'
        ]
        return symbol.upper() in indian_stocks
    
    def _find_similar_symbols(self, symbol, max_suggestions=3):
        
        suggestions = []
        
        major_stocks = {
            'A': ['AAPL', 'AMZN', 'ADBE', 'AMD', 'ABNB'],
            'B': ['BRK-B', 'BAC', 'BABA', 'BLK', 'BA'],
            'C': ['CAT', 'CVX', 'CRM', 'COST', 'CSCO'],
            'G': ['GOOGL', 'GS', 'GM', 'GILD', 'GE'],
            'I': ['INTC', 'IBM', 'INFY', 'ISRG', 'INTU'],
            'J': ['JPM', 'JNJ', 'JD', 'JMIA', 'JBL'],
            'M': ['MSFT', 'META', 'MCD', 'MA', 'MRK'],
            'N': ['NVDA', 'NFLX', 'NKE', 'NVO', 'NSRGY'],
            'P': ['PEP', 'PFE', 'PYPL', 'PG', 'PLTR'],
            'R': ['RELIANCE.NS', 'RIL', 'RDS-A', 'RY', 'RACE'],
            'T': ['TSLA', 'TATASTEEL.NS', 'TATAMOTORS.NS', 'TCS.NS', 'TM'],
            'U': ['UBER', 'UBS', 'ULTA', 'UNH', 'UPS'],
            'W': ['WMT', 'WFC', 'WBD', 'WDAY', 'WBA']
        }
        
        first_letter = symbol[0].upper() if symbol else ''
        if first_letter in major_stocks:
            for stock in major_stocks[first_letter][:max_suggestions]:
                suggestions.append({
                    'original': symbol,
                    'suggestion': stock,
                    'confidence': 'LOW',
                    'reason': f"Similar first letter ({first_letter})"
                })
        
        return suggestions
    
    def get_exchange_info(self, symbol):
        try:
            ticker = self._get_ticker(symbol)
            if not ticker:
                return None
            
            info = ticker.info
            
            exchange_info = {
                'symbol': symbol.upper(),
                'exchange': info.get('exchange', 'Unknown'),
                'exchange_full': info.get('fullExchangeName', 'Unknown'),
                'market': info.get('market', 'Unknown'),
                'timezone': info.get('timeZoneFullName', 'Unknown'),
                'currency': info.get('currency', 'Unknown'),
                'is_tradable': info.get('tradable', False)
            }
            
            if exchange_info['exchange'] == 'NSI' or '.NS' in symbol:
                exchange_info['suffix_required'] = True
                exchange_info['suffix'] = '.NS'
                exchange_info['note'] = 'Indian stocks require .NS suffix (e.g., TCS.NS)'
            elif exchange_info['exchange'] == 'BSE':
                exchange_info['suffix_required'] = True
                exchange_info['suffix'] = '.BO'
                exchange_info['note'] = 'Indian BSE stocks require .BO suffix'
            else:
                exchange_info['suffix_required'] = False
                exchange_info['suffix'] = 'None'
                exchange_info['note'] = 'No special suffix required'
            
            logger.info(f" Exchange info for {symbol}: {exchange_info['exchange']}")
            return exchange_info
            
        except Exception as e:
            logger.error(f"Error getting exchange info for {symbol}: {e}")
            return None
    
    def batch_validate_with_suggestions(self, symbols):
        report = {
            'total_symbols': len(symbols),
            'valid_symbols': [],
            'invalid_symbols': [],
            'suggestions': {},
            'summary': {}
        }
        
        for symbol in symbols:
            if self.validate_symbol(symbol):
                report['valid_symbols'].append(symbol)
            else:
                report['invalid_symbols'].append(symbol)
                suggestions = self.suggest_correction(symbol)
                report['suggestions'][symbol] = suggestions
        
        report['summary'] = {
            'valid_count': len(report['valid_symbols']),
            'invalid_count': len(report['invalid_symbols']),
            'success_rate': f"{(len(report['valid_symbols'])/len(symbols)*100):.1f}%" if symbols else "0%"
        }
        
        return report