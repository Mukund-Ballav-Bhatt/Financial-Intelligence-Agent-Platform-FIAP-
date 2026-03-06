import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def get_news(company):
    try:
        url = "https://newsapi.org/v2/everything"

        params = {
            "q": company,
            "apiKey": NEWS_API_KEY,
            "pageSize": 5,
            "sortBy": "publishedAt"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        articles = data["articles"]
        headlines = [article["title"] for article in articles]

        return headlines

    except Exception as e:
        print("News fetch error:", e)
        return []