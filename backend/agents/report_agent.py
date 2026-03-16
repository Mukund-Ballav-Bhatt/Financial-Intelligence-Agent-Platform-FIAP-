class ReportAgent:

    def generate(self,ticker,price,indicators,sentiment):
        rsi=indicators["RSI"]
        ma=indicators["MA14"]
        vol=indicators["volatility"]

        sentiment_label=sentiment["sentiment"]

        if rsi<30:
            recommendation="BUY"
        elif rsi>70:
            recommendation="SELL"
        else:
            recommendation="HOLD"

        report=f"""
        Stock Analysis Report

Ticker: {ticker}
Current Price: ${price}

Technical Indicators
RSI: {round(rsi,2)}
Moving Average (14): {round(ma,2)}
Volatility: {round(vol,4)}

Market Sentiment: {sentiment_label}

Recommendation: {recommendation}

Summary:
The stock currently shows an RSI of {round(rsi,2)} indicating momentum conditions.
Market sentiment from recent news is {sentiment_label.lower()}.
Based on the indicators, the system suggests a {recommendation} stance.
"""

        return report