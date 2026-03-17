"""
Company Information Operations
Handles fetching company details, financials, and analyst recommendations
"""

import logging
from .base import BaseStockFetcher

logger = logging.getLogger(__name__)

class CompanyOperations(BaseStockFetcher):
    def get_company_info(self, symbol):
        try:
            logger.info(f"Fetching company info for {symbol}...")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                logger.error(f"Could not create ticker for {symbol}")
                return None
            
            info = ticker.info
            
            company_info = {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'N/A'),
                'website': info.get('website', 'N/A'),
                'description': info.get('longBusinessSummary', 'No description available'),
                'employees': info.get('fullTimeEmployees', 0),
                'exchange': info.get('exchange', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'city': info.get('city', 'N/A'),
                'phone': info.get('phone', 'N/A'),
                'address': info.get('address1', 'N/A'),
                
                'ipo_date': info.get('ipoDate', 'N/A'),
                'founded': info.get('founded', 'N/A'),
                
                'ceo': info.get('ceo', info.get('companyOfficers', [{}])[0].get('name', 'N/A') if info.get('companyOfficers') else 'N/A'),
                
                'market': info.get('market', 'N/A'),
                'timezone': info.get('timeZoneFullName', 'N/A'),
                
                'audit_risk': info.get('auditRisk', 'N/A'),
                'board_risk': info.get('boardRisk', 'N/A'),
                'compensation_risk': info.get('compensationRisk', 'N/A')
            }
            
            logger.info(f" Retrieved company info for {symbol}: {company_info['name']}")
            return company_info
            
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return None
    
    def get_key_financials(self, symbol):
        try:
            logger.info(f"Fetching financials for {symbol}...")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                return None
            
            info = ticker.info
            
            financials = {
                'symbol': symbol.upper(),
                
                'valuation': {
                    'market_cap': info.get('marketCap', 0),
                    'enterprise_value': info.get('enterpriseValue', 0),
                    'pe_ratio': info.get('trailingPE', info.get('forwardPE', 0)),
                    'forward_pe': info.get('forwardPE', 0),
                    'peg_ratio': info.get('pegRatio', 0),
                    'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                    'price_to_book': info.get('priceToBook', 0),
                    'enterprise_to_revenue': info.get('enterpriseToRevenue', 0),
                    'enterprise_to_ebitda': info.get('enterpriseToEbitda', 0),
                },
                
                'financial_health': {
                    'total_cash': info.get('totalCash', 0),
                    'total_cash_per_share': info.get('totalCashPerShare', 0),
                    'total_debt': info.get('totalDebt', 0),
                    'debt_to_equity': info.get('debtToEquity', 0),
                    'current_ratio': info.get('currentRatio', 0),
                    'quick_ratio': info.get('quickRatio', 0),
                    'revenue': info.get('totalRevenue', 0),
                    'gross_profit': info.get('grossProfits', 0),
                    'ebitda': info.get('ebitda', 0),
                },
                
                'profitability': {
                    'profit_margin': info.get('profitMargins', 0),
                    'operating_margin': info.get('operatingMargins', 0),
                    'return_on_assets': info.get('returnOnAssets', 0),
                    'return_on_equity': info.get('returnOnEquity', 0),
                    'earnings_growth': info.get('earningsGrowth', 0),
                    'revenue_growth': info.get('revenueGrowth', 0),
                },
                
                'per_share': {
                    'eps': info.get('trailingEps', 0),
                    'forward_eps': info.get('forwardEps', 0),
                    'book_value': info.get('bookValue', 0),
                    'revenue_per_share': info.get('revenuePerShare', 0),
                },
                
                'dividends': {
                    'dividend_rate': info.get('dividendRate', 0),
                    'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                    'payout_ratio': info.get('payoutRatio', 0),
                    'ex_dividend_date': info.get('exDividendDate', 'N/A'),
                },
                
                'trading_info': {
                    'beta': info.get('beta', 0),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                    '52_week_low': info.get('fiftyTwoWeekLow', 0),
                    '50_day_ma': info.get('fiftyDayAverage', 0),
                    '200_day_ma': info.get('twoHundredDayAverage', 0),
                    'avg_volume': info.get('averageVolume', 0),
                    'avg_volume_10day': info.get('averageVolume10days', 0),
                }
            }
            
            if financials['trading_info']['52_week_high'] > 0 and financials['trading_info']['52_week_low'] > 0:
                current_price = info.get('regularMarketPrice', 0)
                if current_price:
                    pct_of_high = (current_price / financials['trading_info']['52_week_high']) * 100
                    pct_of_low = (current_price / financials['trading_info']['52_week_low']) * 100
                    financials['trading_info']['pct_of_52_week_high'] = round(pct_of_high, 1)
                    financials['trading_info']['pct_of_52_week_low'] = round(pct_of_low, 1)
            
            logger.info(f" Retrieved financials for {symbol}")
            return financials
            
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            return None
    
    def get_analyst_recommendations(self, symbol):
        try:
            logger.info(f"Fetching analyst recommendations for {symbol}...")
            
            ticker = self._get_ticker(symbol)
            if not ticker:
                return None
            
            recommendations = ticker.recommendations
            
            info = ticker.info
            target_data = {
                'target_high': info.get('targetHighPrice', 0),
                'target_low': info.get('targetLowPrice', 0),
                'target_mean': info.get('targetMeanPrice', 0),
                'target_median': info.get('targetMedianPrice', 0),
                'number_of_analysts': info.get('numberOfAnalystOpinions', 0),
                'recommendation': info.get('recommendationKey', 'N/A'),
                'recommendation_mean': info.get('recommendationMean', 0)
            }
            
            historical = []
            if recommendations is not None and not recommendations.empty:
                for idx, row in recommendations.tail(5).iterrows():
                    historical.append({
                        'date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                        'to_grade': row.get('To Grade', 'N/A'),
                        'from_grade': row.get('From Grade', 'N/A'),
                        'action': row.get('Action', 'N/A')
                    })
            
            if target_data['target_mean'] > 0 and info.get('regularMarketPrice', 0) > 0:
                current_price = info.get('regularMarketPrice', 0)
                upside = ((target_data['target_mean'] - current_price) / current_price) * 100
                target_data['potential_upside'] = round(upside, 1)
            
            result = {
                'symbol': symbol.upper(),
                'current_price': info.get('regularMarketPrice', 0),
                'target_prices': target_data,
                'consensus': target_data.get('recommendation', 'N/A'),
                'historical_recommendations': historical,
                'summary': self._generate_recommendation_summary(target_data)
            }
            
            logger.info(f" Retrieved analyst data for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching recommendations for {symbol}: {e}")
            return None
    
    def _generate_recommendation_summary(self, target_data):
        if not target_data or target_data['target_mean'] == 0:
            return "Insufficient analyst data"
        
        rec = target_data.get('recommendation', '').lower()
        
        if rec in ['strong_buy', 'buy']:
            return "Analysts are BULLISH on this stock"
        elif rec == 'hold':
            return "Analysts recommend HOLDING this stock"
        elif rec in ['sell', 'strong_sell']:
            return "Analysts are BEARISH on this stock"
        else:
            return f"Mixed analyst opinions (mean: {target_data.get('recommendation_mean', 'N/A')})"
    
    def get_insider_transactions(self, symbol):
        try:
            ticker = self._get_ticker(symbol)
            if not ticker:
                return None
            
            insider = ticker.insider_transactions
            
            if insider is None or insider.empty:
                logger.info(f"No insider transaction data for {symbol}")
                return []
            
            result = []
            for idx, row in insider.head(5).iterrows():
                result.append({
                    'date': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'shares': int(row.get('Shares', 0)),
                    'value': float(row.get('Value', 0)),
                    'transaction': row.get('Transaction', 'N/A')
                })
            
            logger.info(f"Retrieved {len(result)} insider transactions for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching insider transactions for {symbol}: {e}")
            return []
    
    def get_company_summary(self, symbol):
        info = self.get_company_info(symbol)
        financials = self.get_key_financials(symbol)
        
        if not info:
            return None
        
        summary = {
            'symbol': symbol.upper(),
            'company_name': info.get('name', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'country': info.get('country', 'N/A'),
            'description': info.get('description', '')[:200] + '...' if len(info.get('description', '')) > 200 else info.get('description', ''),
            'website': info.get('website', 'N/A'),
        }
        
        if financials:
            summary['market_cap'] = financials['valuation'].get('market_cap', 0)
            summary['pe_ratio'] = financials['valuation'].get('pe_ratio', 0)
            summary['dividend_yield'] = financials['dividends'].get('dividend_yield', 0)
            summary['52_week_high'] = financials['trading_info'].get('52_week_high', 0)
            summary['52_week_low'] = financials['trading_info'].get('52_week_low', 0)
        
        return summary