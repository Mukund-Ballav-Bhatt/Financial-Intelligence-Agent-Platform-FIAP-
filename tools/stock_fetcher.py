import yfinance as yf

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.history(period="1d")
        price = info["Close"].iloc[-1]
        return round(price, 2)

    except Exception as e:
        print("Stock fetch error:", e)
        return None