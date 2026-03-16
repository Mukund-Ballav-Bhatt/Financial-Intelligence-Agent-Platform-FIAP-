from fastapi import FastAPI
from agents.orchestrator import StockAnalysisPipeline
from models.response_models import StockAnalysisResponse

app=FastAPI()

pipeline=StockAnalysisPipeline()

@app.get("/")
def home():
     return {"message": "AI Financial Stock Analyzer API"}

@app.get("/analyze/{ticker}", response_model=StockAnalysisResponse)
def analyze_stock(ticker: str):

    result = pipeline.run(ticker)

    return result