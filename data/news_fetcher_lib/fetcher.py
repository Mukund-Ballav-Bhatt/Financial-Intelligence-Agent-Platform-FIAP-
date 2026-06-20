import logging
from datetime import datetime, timedelta
from .base import BaseNewsFetcher

logger = logging.getLogger(__name__)


class NewsFetcherOperations(BaseNewsFetcher):
    def __init__(self, api_key=None):
        super().__init__(api_key)
        self.base_url = "https://newsapi.org/v2"

    def fetch_news_by_symbol(self, symbol, days_back=3, page_size=10):
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

            params = {
                'q': symbol,
                'from': from_date,
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': page_size
            }

            url = f"{self.base_url}/everything"
            data = self._make_request(url, params)

            if not data or data.get('status') != 'ok':
                logger.error(f"Failed to fetch news for {symbol}")
                return []

            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'symbol': symbol,
                    'headline': article.get('title', ''),
                    'content': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'author': article.get('author', ''),
                    'url': article.get('url', ''),
                    'url_to_image': article.get('urlToImage', ''),
                    'published_date': article.get('publishedAt', datetime.now().isoformat())
                })

            logger.info(f"Fetched {len(articles)} articles for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def fetch_multiple_symbols(self, symbols, days_back=3, page_size=5, delay=1):
        results = {}

        for i, symbol in enumerate(symbols):
            logger.info(f"Fetching news for {symbol} ({i+1}/{len(symbols)})")
            articles = self.fetch_news_by_symbol(symbol, days_back, page_size)
            results[symbol] = articles
            self._delay(delay)

        return results

    def fetch_top_headlines(self, category='business', country='us', page_size=10):
        try:
            params = {
                'category': category,
                'country': country,
                'pageSize': page_size
            }

            url = f"{self.base_url}/top-headlines"
            data = self._make_request(url, params)

            if not data or data.get('status') != 'ok':
                logger.error("Failed to fetch top headlines")
                return []

            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'headline': article.get('title', ''),
                    'content': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_date': article.get('publishedAt', datetime.now().isoformat())
                })

            logger.info(f"Fetched {len(articles)} top headlines")
            return articles

        except Exception as e:
            logger.error(f"Error fetching top headlines: {e}")
            return []