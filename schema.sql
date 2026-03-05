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
    symbol TEXT NOT NULL,                   -- Stock identifier

    price REAL NOT NULL,                    -- Current Price
    change REAL,                            -- Diference between prev and curr eg- +1.5
    change_percent REAL,
    volume INTEGER,                         -- No of shares today
    open REAL,                              -- Price when market open today
    high REAL,                              -- Highest price reached today 
    low REAL,                               -- Lowest price reached today 
    market_price REAL,                      -- Value of company i.e. price * shares 
    pe__ratio REAL,                         -- Price to Earning Ratio
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,       -- When this data was Fetched

    currency TEXT DEFAULT 'USD',
    data_source TEXT DEFAULT 'yfinance'
);

CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    symbol TEXT NOT NULL,
    
    headline TEXT NOT NULL,              
    content TEXT,                     
    source TEXT,                         
    author TEXT,                         
    
    url TEXT UNIQUE,                      -- Link to full article
    url_to_image TEXT,                     -- Link to article image
    
    published_date DATETIME,              
    fetched_date DATETIME DEFAULT CURRENT_TIMESTAMP,  
    
    language TEXT DEFAULT 'en',
    is_duplicate BOOLEAN DEFAULT 0        -- Flag for duplicate detection
);

-- ============================================
-- TABLE 3: sentiment_analysis
-- Stores sentiment analysis results from LLM
-- Links to news_articles table
-- ============================================

CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    news_id INTEGER NOT NULL,           --Foreign key for news-article
    
    sentiment TEXT NOT NULL CHECK(
        sentiment IN ('positive', 'neutral', 'negative', 'mixed')  -- Allowed Values
    ),
    confidence REAL CHECK(confidence >= 0 AND confidence <= 1),     -- LLM tells whether its right or wrong
    
    positive_score REAL DEFAULT 0,          -- Positive sentiment
    negative_score REAL DEFAULT 0,          -- Negetive sentiment
    neutral_score REAL DEFAULT 0,

    /*Example 1 (Strongly Positive):
    positive_score: 0.85
    negative_score: 0.10  
    neutral_score:  0.05
    → sentiment: 'positive'

    Example 2 (Mixed):
    positive_score: 0.45
    negative_score: 0.40
    neutral_score:  0.15
    → sentiment: 'mixed'

    Example 3 (Neutral):
    positive_score: 0.20
    negative_score: 0.15
    neutral_score:  0.65
    → sentiment: 'neutral'
    */
    
    analyzed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_used TEXT DEFAULT 'llama3.2',
    analysis_version TEXT DEFAULT '1.0',
    
    FOREIGN KEY (news_id) REFERENCES news_articles(id) ON DELETE CASCADE    -- Foreign Key relationship , Delete from both
);

/*
news_articles                    sentiment_analysis
-------------                    ------------------
id: 1  <─── foreign key ───>    news_id: 1
headline: "Apple good"            sentiment: "positive"
                                  confidence: 0.95

id: 2  <─── foreign key ───>    news_id: 2
headline: "Apple bad"             sentiment: "negative"
                                  confidence: 0.87

id: 3                              (no sentiment yet)
headline: "Apple neutral"
*/


CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    symbol TEXT NOT NULL,
    
    price REAL,
    price_change REAL,
    sentiment_summary TEXT,      -- Overall sentiment (positive/neutral/negative)
    
    -- LLM generated content
    news_summary TEXT,           -- Summarized news (200-300 words)
    full_report TEXT,            -- Complete report in markdown format
    key_points TEXT,             -- Bullet points as JSON string , For Dashboard use
    
    generated_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    report_version TEXT DEFAULT '1.0',
    is_draft BOOLEAN DEFAULT 0,
    
    tags TEXT                     -- Comma-separated tags , For Dashboard to fiilter 
);

-- Speed up stock symbol searches
CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_timestamp ON stock_prices(timestamp);

-- Speed up news queries
CREATE INDEX IF NOT EXISTS idx_news_symbol ON news_articles(symbol);
CREATE INDEX IF NOT EXISTS idx_news_date ON news_articles(published_date);
CREATE INDEX IF NOT EXISTS idx_news_symbol_date ON news_articles(symbol, published_date);

-- Speed up sentiment lookups
CREATE INDEX IF NOT EXISTS idx_sentiment_news ON sentiment_analysis(news_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_result ON sentiment_analysis(sentiment);

-- Speed up report queries
CREATE INDEX IF NOT EXISTS idx_reports_symbol ON reports(symbol);
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(generated_date);
CREATE INDEX IF NOT EXISTS idx_reports_symbol_date ON reports(symbol, generated_date);