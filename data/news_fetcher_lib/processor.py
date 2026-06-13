import logging
import re
from datetime import datetime
from .base import BaseNewsFetcher

logger = logging.getLogger(__name__)


class NewsProcessor(BaseNewsFetcher):
    def __init__(self, api_key=None):
        super().__init__(api_key)

    def clean_text(self, text):
        if not text:
            return ""
        
        text = re.sub(r'[^\w\s\.\,\!\?\-\']', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_keywords(self, text, max_keywords=5):
        if not text:
            return []
        
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]

    def process_articles(self, articles):
        processed = []
        
        for article in articles:
            if not article.get('headline'):
                continue
            
            processed_article = {
                'headline': self.clean_text(article.get('headline', '')),
                'content': self.clean_text(article.get('content', '')),
                'source': article.get('source', 'Unknown'),
                'author': article.get('author', 'Unknown'),
                'url': article.get('url', ''),
                'published_date': article.get('published_date', datetime.now().isoformat()),
                'keywords': []
            }
            
            if processed_article['content']:
                processed_article['keywords'] = self.extract_keywords(processed_article['content'])
            
            processed.append(processed_article)
        
        logger.info(f"Processed {len(processed)} articles")
        return processed

    def filter_by_relevance(self, articles, symbol):
        relevant = []
        
        for article in articles:
            headline = article.get('headline', '').lower()
            content = article.get('content', '').lower()
            symbol_lower = symbol.lower()
            
            if symbol_lower in headline or symbol_lower in content:
                relevant.append(article)
        
        logger.info(f"Filtered {len(relevant)}/{len(articles)} relevant articles for {symbol}")
        return relevant

    def get_article_summary(self, article, max_length=200):
        content = article.get('content', '')
        if len(content) > max_length:
            content = content[:max_length] + '...'
        
        return {
            'headline': article.get('headline', ''),
            'summary': content,
            'source': article.get('source', ''),
            'date': article.get('published_date', ''),
            'keywords': article.get('keywords', [])
        }