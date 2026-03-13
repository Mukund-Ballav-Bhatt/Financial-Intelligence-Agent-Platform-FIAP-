from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.market_agent import get_market_data
from backend.agents.news_agent import get_news
from backend.agents.sentiment_agent import get_sentiment
from backend.agents.planner_agent import generate_report

app = FastAPI()

# Allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/market")
def market(ticker: str):
    return get_market_data(ticker)

@app.get("/news")
def news(ticker: str):
    return get_news(ticker)

@app.get("/sentiment")
def sentiment(ticker: str):
    news_data = get_news(ticker)
    return get_sentiment(news_data)

@app.get("/report")
def report(ticker: str):
    return generate_report(ticker)

@app.get("/")
def home():
    return {"message": "Financial Intelligence API Running"}