from tools.stock_fetcher import get_stock_data
from tools.news_fetcher import get_news

from backend.agents.report_agent import ReportAgent
from backend.agents.analysis_agent import AnalysisAgent
from backend.agents.sentiment_agent import SentimentAgent
from backend.agents.strategy_agent import StrategyAgent

from backend.utils.logger import logger

from functools import lru_cache
import yfinance as yf


class StockAnalysisPipeline:

    def __init__(self):

        self.analysis_agent = AnalysisAgent()
        self.sentiment_agent = SentimentAgent()
        self.report_agent = ReportAgent()
        self.strategy_agent = StrategyAgent()


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

        stock_data = get_stock_data(ticker)

        if stock_data is None or "price" not in stock_data:
            return {"error": "Stock data not available"}

        logger.info("Stock data fetched")

        news = get_news(ticker)

        indicators = self.analysis_agent.analyse(stock_data)

        logger.info("Indicators calculated")

        sentiment = self.sentiment_agent.analyze(news)

        logger.info("Sentiment calculated")

        signal = self.strategy_agent.generate_signal(
            indicators,
            sentiment
        )

        report = self.report_agent.generate(
            ticker,
            float(stock_data["price"]),
            indicators,
            sentiment
        )

        logger.info("Report generated")

        chart_data = self.get_chart_data(ticker)

        result = {
            "ticker": ticker,
            "price": stock_data["price"],
            "indicators": indicators,
            "sentiment": sentiment,
            "signal": signal,
            "news": news,
            "report": report,
            "chart": chart_data
        }

        return result