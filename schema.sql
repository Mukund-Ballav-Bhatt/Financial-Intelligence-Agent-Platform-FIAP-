/*We will have 3 tables:

1) stock_prices - Current and historical prices
2) news_articles - News article about stocks
3) sentiment_analysis - Analysis results from LLM

And we will generate a report based on these 3 to send to dashboard

We use **SQL Lite** as we don't have to do (i) Gazzilion transaction/sec
                                       (ii) No concurrent Writters 
                                       (iii) No remote content
                                       (iv) No big data

*/
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT , 
    symbol TEXT NOT NULL
)