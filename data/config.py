import os
import logging 
from datetime import datetime
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = CURRENT_DIR

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    print("⚠️  WARNING: NEWS_API_KEY not found!")
else:
    masked_key =   NEWS_API_KEY[:4] + "*" * (len( NEWS_API_KEY) - 4)         #Masking and showing first 4 Characters
    print(f"✅ News API Key loaded: {masked_key}")

URL = 'https://newsapi.org'
API_TIMEOUT = 10

DB_PATH = os.path.join(PROJECT_ROOT, 'financial_data.db')
print(f"💾 Database will be stored at: {DB_PATH}")

DB_TIMEOUT = 30  
DB_ISOLATION_LEVEL = None  

MAX_NEWS_ARTICLES = 5   
NEWS_DAYS_BACK = 3 
NEWS_CACHE_MINUTES = 15    

MAX_RETRIES = 3             #Retry Settings
RETRY_DELAY_SECONDS = 2     

REQUEST_TIMEOUT = 30        # Maximum seconds to wait for API response
USER_AGENT = "Financial-Data-Service/1.0" 

if __name__ == "__main__":
    
    print(f"   Config location: {CURRENT_DIR}")
    print(f"   Database path: {DB_PATH}")
    
    print("\n🔑 API KEYS:")
    print(f"   News API Key: {'✅ Set' if NEWS_API_KEY else '❌ Missing'}")
    
    print("\n⚙️ SETTINGS:")
    print(f"   Max news articles: {MAX_NEWS_ARTICLES}")
    print(f"   News days back: {NEWS_DAYS_BACK}")
    print(f"   Max retries: {MAX_RETRIES}")
    print(f"   Timeout: {REQUEST_TIMEOUT} seconds")

DEFAULT_SYMBOLS = ['GOOGL' ,'AAPL' ,'AMZN' , 'TSLA' , 'MSFT']
print(f"SYMBOLS ALLOWED {', '.join(DEFAULT_SYMBOLS)}")

ADDITIONAL_SYMBOLS = ['META', 'NVDA', 'JPM', 'V', 'JNJ']
ALL_SYMBOLS = DEFAULT_SYMBOLS + ADDITIONAL_SYMBOLS

# Stock price validation
MIN_STOCK_PRICE = 0.01      
MAX_STOCK_PRICE = 1000000   
MAX_PRICE_CHANGE_PERCENT = 100
MAX_DAILY_VOLUME = 10000000000          #All this data is from investopedia
# News validation
MIN_HEADLINE_LENGTH = 5 
MAX_HEADLINE_LENGTH = 300    
MAX_CONTENT_LENGTH = 5000   

DATE_DISPLAY_FORMAT = '%Y-%m-%d %H:%M:%S' 
DATE_SHORT_FORMAT = '%Y-%m-%d'            
CURRENCY_SYMBOL = '$'
PERCENTAGE_SYMBOL = '%'

# US stock market hours (Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0
MARKET_TIMEZONE = 'US/Eastern'
#Logging
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    print(f"📁 Created logs directory: {LOG_DIR}")

today = datetime.now().strftime('%Y%m%d')
LOG_FILE = os.path.join(LOG_DIR, f'data_service_{today}.log')
print(f"📝 Log file: {LOG_FILE}")

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),  
        logging.StreamHandler()          
    ]
)

logger = logging.getLogger(__name__)

logger.info("=" * 50)
logger.info("🚀 Financial Data Service Configuration Loaded")
logger.info("=" * 50)
logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Database: {DB_PATH}")
logger.info(f"Tracking {len(DEFAULT_SYMBOLS)} stocks: {', '.join(DEFAULT_SYMBOLS)}")
