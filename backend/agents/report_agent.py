class ReportAgent:

    def generate(self, ticker, price, indicators, sentiment, signal):

        report = f"""
Stock Analysis Report

Ticker: {ticker}
Current Price: ${price}

Technical Indicators
RSI: {round(indicators['RSI'], 2)}
Moving Average (14): {round(indicators['MA14'], 2)}
Volatility: {round(indicators['volatility'], 4)}

Market Sentiment: {sentiment['sentiment']}

Recommendation: {signal['signal']}

Summary:
The stock shows an RSI of {round(indicators['RSI'], 2)}.
Market sentiment is {sentiment['sentiment'].lower()}.
Final recommendation is {signal['signal']}.
"""

        return report