import logging
from datetime import datetime
from .base import BaseNewsFetcher
from .fetcher import NewsFetcherOperations
from .processor import NewsProcessor

logger = logging.getLogger(__name__)


class NewsFetcher(NewsFetcherOperations, NewsProcessor, BaseNewsFetcher):
    def __init__(self, api_key=None):
        super().__init__(api_key)
        logger.info("NewsFetcher fully initialized")

    def fetch_and_process(self, symbol, days_back=3, page_size=10):
        articles = self.fetch_news_by_symbol(symbol, days_back, page_size)
        
        if not articles:
            return []
        
        processed = self.process_articles(articles)
        relevant = self.filter_by_relevance(processed, symbol)
        
        return relevant

    def fetch_multiple_and_process(self, symbols, days_back=3, page_size=5, delay=1):
        results = {}
        
        for symbol in symbols:
            articles = self.fetch_and_process(symbol, days_back, page_size)
            results[symbol] = articles
            self._delay(delay)
        
        return results

    def get_news_with_sentiment_ready(self, symbol, days_back=3, page_size=10):
        articles = self.fetch_and_process(symbol, days_back, page_size)
        
        ready_articles = []
        for article in articles:
            ready_articles.append({
                'symbol': symbol,
                'headline': article['headline'],
                'content': article['content'],
                'source': article['source'],
                'url': article['url'],
                'published_date': article['published_date'],
                'keywords': article['keywords']
            })
        
        return ready_articles

    def get_recent_news_summary(self, symbol, days_back=3, limit=5):
        articles = self.fetch_and_process(symbol, days_back, limit)
        
        summaries = []
        for article in articles[:limit]:
            summaries.append(self.get_article_summary(article))
        
        return summaries