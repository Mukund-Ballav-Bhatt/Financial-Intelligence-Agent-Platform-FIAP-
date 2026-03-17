import logging
from .base import BaseStockFetcher
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HistoricalOperations(BaseStockFetcher):
    def get_historical_data(self, symbol, period="1mo", interval="1d"):
        try:
            logger.info(f"Fetching historical data for {symbol} (period={period}, interval={interval})")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                logger.error(f"Could not create ticker for {symbol}")
                return []
            
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol} with period={period}")
                return []
            
            result = []
            for date, row in hist.iterrows():
                result.append({
                    'symbol': symbol,
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })
            
            logger.info(f" Retrieved {len(result)} historical records for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def get_price_trend(self, symbol, days=30):
        if days <= 5:
            period = "5d"
        elif days <= 30:
            period = "1mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 180:
            period = "6mo"
        else:
            period = "1y"
        
        data = self.get_historical_data(symbol, period=period)
        
        if not data or len(data) < 2:
            logger.warning(f"Not enough historical data for {symbol} trend analysis")
            return None
        
        first_price = data[-1]['close']  
        last_price = data[0]['close']     
        
        prices = [d['close'] for d in data]
        high = max(prices)
        low = min(prices)
        high_date = data[prices.index(high)]['date']
        low_date = data[prices.index(low)]['date']
        
        daily_ranges = [(d['high'] - d['low']) / d['low'] * 100 for d in data]
        avg_volatility = sum(daily_ranges) / len(daily_ranges)
        
        if last_price > first_price:
            trend_direction = "UP"
        elif last_price < first_price:
            trend_direction = "DOWN"
        else:
            trend_direction = "FLAT"
        
        result = {
            'symbol': symbol,
            'analysis_period': f"Last {len(data)} trading days",
            'start_date': data[-1]['date'],
            'end_date': data[0]['date'],
            'start_price': first_price,
            'end_price': last_price,
            'price_change': round(last_price - first_price, 2),
            'change_percent': round(((last_price - first_price) / first_price) * 100, 2),
            'trend_direction': trend_direction,
            'period_high': {
                'price': high,
                'date': high_date
            },
            'period_low': {
                'price': low,
                'date': low_date
            },
            'volatility': round(avg_volatility, 2),
            'data_points': len(data)
        }
        
        logger.info(f" Trend analysis for {symbol}: {result['change_percent']}% over {len(data)} days")
        return result
    
    def get_moving_average(self, symbol, days=20):
        period = f"{days*2}d"
        data = self.get_historical_data(symbol, period=period)
        
        if not data or len(data) < days:
            logger.warning(f"Not enough data for {days}-day moving average for {symbol}")
            return None
        
        recent = data[:days]
        closes = [d['close'] for d in recent]
        ma_value = sum(closes) / len(closes)
        
        current_price = data[0]['close']
        
        result = {
            'symbol': symbol,
            'ma_type': f"{days}-day Simple Moving Average",
            'ma_value': round(ma_value, 2),
            'current_price': current_price,
            'difference': round(current_price - ma_value, 2),
            'difference_percent': round(((current_price - ma_value) / ma_value) * 100, 2),
            'position': "ABOVE" if current_price > ma_value else "BELOW" if current_price < ma_value else "EQUAL",
            'calculation_date': data[0]['date'],
            'days_used': min(days, len(recent))
        }
        
        logger.info(f" {days}-day MA for {symbol}: ${ma_value}")
        return result
    
    def get_multiple_moving_averages(self, symbol, periods=[20, 50, 200]):
        result = {
            'symbol': symbol,
            'current_price': None,
            'moving_averages': {},
            'signals': []
        }
        
        max_period = max(periods)
        data = self.get_historical_data(symbol, period=f"{max_period*2}d")
        
        if not data:
            return None
        
        result['current_price'] = data[0]['close']
        
        for period in periods:
            if len(data) >= period:
                recent = data[:period]
                closes = [d['close'] for d in recent]
                ma_value = sum(closes) / len(closes)
                
                result['moving_averages'][f"{period}_day"] = round(ma_value, 2)
                if result['current_price'] > ma_value:
                    result['signals'].append(f"ABOVE {period}-day MA (BULLISH)")
                else:
                    result['signals'].append(f"BELOW {period}-day MA (BEARISH)")
        
        if '50_day' in result['moving_averages'] and '200_day' in result['moving_averages']:
            if result['moving_averages']['50_day'] > result['moving_averages']['200_day']:
                result['signals'].append("GOLDEN CROSS DETECTED (50 above 200) - BULLISH")
            else:
                result['signals'].append("DEATH CROSS DETECTED (50 below 200) - BEARISH")
        
        return result
    
    def get_daily_returns(self, symbol, days=30):
        period = f"{days}d"
        data = self.get_historical_data(symbol, period=period)
        
        if not data or len(data) < 2:
            return None
        
        returns = []
        for i in range(len(data) - 1):
            daily_return = ((data[i]['close'] - data[i+1]['close']) / data[i+1]['close']) * 100
            returns.append({
                'date': data[i]['date'],
                'return': round(daily_return, 2)
            })
        
        return_values = [r['return'] for r in returns]
        
        result = {
            'symbol': symbol,
            'period': f"Last {len(returns)} trading days",
            'total_return': round(sum(return_values), 2),
            'avg_daily_return': round(sum(return_values) / len(return_values), 2),
            'max_daily_gain': max(return_values),
            'max_daily_loss': min(return_values),
            'positive_days': len([r for r in return_values if r > 0]),
            'negative_days': len([r for r in return_values if r < 0]),
            'daily_returns': returns[:10] 
        }
        
        return result