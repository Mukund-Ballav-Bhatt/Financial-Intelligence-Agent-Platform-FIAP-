from .base import DatabaseBase
from .stocks_ops import StockOperations
from .news_ops import NewsOperations
from .sentiment_ops import SentimentOperations
from .report_ops import ReportOperations

class DatabaseManager(
    StockOperations,
    NewsOperations,
    SentimentOperations,
    ReportOperations,
    DatabaseBase
):
    """
    Complete Database Manager with all operations.
    """
    def __init__(self, path=None):
        # Initialize all parent classes
        super().__init__(path)