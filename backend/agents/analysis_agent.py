import pandas as pd

class AnalysisAgent:

    def moving_average(self, prices, window=14):
        series = pd.Series(prices)
        result = series.rolling(window).mean().iloc[-1]
        # fallback to simple mean if not enough data
        return float(result) if not pd.isna(result) else float(series.mean())

    def volatility(self, prices):
        series = pd.Series(prices)
        result = series.pct_change().std()
        return float(result) if not pd.isna(result) else 0.0

    def rsi(self, prices, window=14):
        series = pd.Series(prices)

        # Need at least window+1 points for a valid RSI
        if len(series) < window + 1:
            print(f"[AnalysisAgent] Warning: only {len(series)} prices, need {window+1} for RSI. Using shorter window.")
            window = max(2, len(series) - 1)  # shrink window to fit available data

        delta = series.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()

        avg_loss = avg_loss.replace(0, 1e-10)

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        result = rsi.iloc[-1]

        # Final NaN guard — return neutral RSI of 50
        return float(result) if not pd.isna(result) else 50.0

    def analyse(self, prices):
        if not prices or len(prices) < 2:
            return {"RSI": 50.0, "MA14": 0.0, "volatility": 0.0}

        return {
            "RSI": self.rsi(prices),
            "MA14": self.moving_average(prices),
            "volatility": self.volatility(prices)
        }