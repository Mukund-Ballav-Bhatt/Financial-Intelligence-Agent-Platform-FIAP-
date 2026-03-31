from tools.news_fetcher import get_news

from backend.agents.report_agent import ReportAgent
from backend.agents.analysis_agent import AnalysisAgent
from backend.agents.sentiment_agent import SentimentAgent
from backend.agents.strategy_agent import StrategyAgent
from backend.agents.llm_agent import summarize_news

from backend.utils.logger import logger

from data.stock_fetcher_lib.manager import StockFetcher
from data.database_lib.manager import DatabaseManager

from functools import lru_cache
import time
import yfinance as yf


class StockAnalysisPipeline:

    def __init__(self):
        self.analysis_agent = AnalysisAgent()
        self.sentiment_agent = SentimentAgent()
        self.report_agent = ReportAgent()
        self.strategy_agent = StrategyAgent()

        self.fetcher = StockFetcher()

        self.db = DatabaseManager()

        self.sentiment_cache = {}
        self.cache_ttl = 300  # 5 minutes

    @lru_cache(maxsize=50)
    def get_cached_quote(self, ticker):
        logger.info(" Using cached stock quote")
        return self.fetcher.get_quote_summary(ticker)
        
    @lru_cache(maxsize=50)
    def get_cached_ma(self, ticker):
        logger.info("⚡ Using cached moving average")
        return self.fetcher.get_moving_average(ticker, days=14)
        
    def get_cached_sentiment(self, ticker, news):
        current_time = time.time()

        if ticker in self.sentiment_cache:
            data, timestamp = self.sentiment_cache[ticker]

            if current_time - timestamp < self.cache_ttl:
                 logger.info("Using cached sentiment")
                 return data

        sentiment = self.sentiment_agent.analyze(news)
        self.sentiment_cache[ticker] = (sentiment, current_time)

        return sentiment

    def get_chart_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")

            chart = []
            for date, row in hist.iterrows():
                chart.append({
                    "day": date.strftime("%a"),
                    "price": round(row["Close"], 2)
                })

            return chart

        except Exception as e:
            logger.error(f"Chart data error: {e}")
            return []

    def run(self, ticker):

        logger.info(f"Starting analysis for {ticker}")

        # 1. Get latest stock price (Person 2)
        logger.info("Fetching stock data")
        quote = self.get_cached_quote(ticker)

        
        from fastapi import HTTPException
        if not quote:
            logger.error(f"No stock data available for {ticker}")
            raise HTTPException(status_code=404, detail=f"No stock data available for {ticker}")

        # 2. Get historical prices (Person 2)
        history = self.db.get_price_hist(ticker, limit=30)

        if not history:
            return {"error": "Not enough historical data"}

        prices = [h["price"] for h in history]

        # 3.  analysis
        indicators = self.analysis_agent.analyse(prices)

        if not indicators:
            return {"error": "Indicator calculation failed"}

        # OPTIONAL: Override MA from Person 2
        ma_data = self.get_cached_ma(ticker)
        if ma_data:
            indicators["MA14"] = ma_data["ma_value"]

        logger.info(f" Indicators calculated: {indicators}")

        # 4. News + Sentiment
        stored_news = self.db.get_news_for_symbol(ticker, limit=10)

        if stored_news:
            logger.info("Using cached news from DB")
            news = [n["headline"] for n in stored_news]
            news_ids = [n["id"] for n in stored_news]

        else:
            logger.info("Fetching fresh news")
            news = get_news(ticker)
            news_ids = []

            for headline in news:
                news_id = self.db.insert_article(
                    symbol=ticker,
                    headline=headline
                )
                if news_id:
                    news_ids.append(news_id)

        sentiment_data = self.db.get_aggregate_sentiment(ticker)

        if sentiment_data and sentiment_data["total_articles"] > 0:
            logger.info(" Using stored sentiment")

            sentiment = {
                "sentiment": sentiment_data["overall_sentiment"].capitalize(),
                "score": sentiment_data["sentiment_score"],
                "articles_analyzed": sentiment_data["total_articles"]
            }

        else:
            logger.info(" Calculating new sentiment")

            sentiment = self.get_cached_sentiment(ticker, news)

            # Save sentiment per article
            for news_id in news_ids:
                self.db.insert_sentiment(
                    news_id=news_id,
                    sentiment=sentiment["sentiment"].lower(),
                    confidence=abs(sentiment["score"])
                )

        logger.info(f"Sentiment: {sentiment}")

        # 5. Strategy
        signal = self.strategy_agent.generate_signal(indicators, sentiment)

        logger.info(f"Signal: {signal}")

        #  LLM NEWS SUMMARY
        news_summary = summarize_news(
            ticker=ticker,
            headlines=news,
            price=float(quote["price"]),
            signal=signal["signal"] if isinstance(signal, dict) else signal
        )

        logger.info(f"News Summary: {news_summary}")

        # 6 Report
        report = self.report_agent.generate(
             ticker,
            float(quote["price"]),
            indicators,
            sentiment,
            signal,
            news_summary   
)
        # 7.  Save Report
        self.db.insert_report(
            symbol=ticker,
            price=quote["price"],
            sentiment_summary=sentiment["sentiment"],
            full_report=report,
            tags=signal["signal"]
        )

        # 8. Chart
        chart_data = self.get_chart_data(ticker)

        return {
            "ticker": ticker,
            "price": quote["price"],
            "indicators": indicators,
            "sentiment": sentiment,
            "signal": signal,
            "news": news,
            "report": report,
            "chart": chart_data
        }