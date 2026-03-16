from tools.stock_fetcher import get_stock_data
from tools.news_fetcher import get_news



from agents.report_agent import ReportAgent
from agents.analysis_agent import AnalysisAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent import StrategyAgent

from utils.logger import logger


from functools import lru_cache

class StockAnalysisPipeline:

    def __init__(self):
        self.analysis_agent=AnalysisAgent()
        self.sentiment_agent=SentimentAgent()
        self.report_agent=ReportAgent()
        self.strategy_agent=StrategyAgent()
    
    @lru_cache(maxsize=50)
    def run(self,ticker):
        logger.info(f"Starting analysis for {ticker}")

        stock_data=get_stock_data(ticker)

        if stock_data is None or "price" not in stock_data:
            return{"error":"Stock data not available"}
        
        logger.info("Stock data fetched")

        news = get_news(ticker)

        indicators=self.analysis_agent.analyse(stock_data)

        logger.info("Indicators calculated")

        sentiment=self.sentiment_agent.analyze(news)
        
        logger.info("Sentiment calculated")

        report=self.report_agent.generate(
            ticker,
            float(stock_data["price"]),
            indicators,
            sentiment
        )
        logger.info("Report generated successfully"
                    )
        signal=self.strategy_agent.generate_signal(
            indicators,
            sentiment
        )
        result={
            "ticker":ticker,
            "price":stock_data["price"],
            "indicators":indicators,
            "sentiment":sentiment,
            "signal":signal,
            "news": news,
            "report":report
        }

        return result
         