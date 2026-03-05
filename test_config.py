import os
import sys
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):

    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"   📌 {text}")

print_header("TEST 1: Importing Configuration")
    
try:
    import config
    print_success("Successfully imported config")
except Exception as e:
    print_error(f"Failed to import config: {e}")
    sys.exit(1)

print_header("TEST 2: Python Version")

python_version = sys.version_info
print_info(f"Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major >= 3 and python_version.minor >= 7:
    print_success("Python version is compatible (3.7+)")
else:
    print_warning("Python version is older than 3.7 - consider upgrading")

print_header("TEST 3: Environment & Paths")

current_dir = os.getcwd()
print_info(f"Current directory: {current_dir}")

config_path = os.path.join(current_dir, 'config.py')
if os.path.exists(config_path):
    print_success("config.py found in current directory")
else:
    print_error("config.py not found in current directory")

env_path = os.path.join(current_dir, '.env')
if os.path.exists(env_path):
    print_success(".env file found")
    
    with open(env_path, 'r') as f:
        first_line = f.readline().strip()
        if first_line and '=' in first_line:
            print_success(".env file has content")
        else:
            print_warning(".env file appears empty")
else:
    print_warning(".env file not found - API keys won't work")

print_header("TEST 4: API Keys")

if hasattr(config, 'NEWS_API_KEY'):
    if config.NEWS_API_KEY:
        masked_key = config.NEWS_API_KEY[:4] + '*' * 4
        print_success(f"News API Key: {masked_key}")
    else:
        print_warning("News API Key is empty")
else:
    print_error("NEWS_API_KEY not found in config")

print_header("TEST 5: Database Settings")

if hasattr(config, 'DB_PATH'):
    print_info(f"Database path: {config.DB_PATH}")
    
    db_dir = os.path.dirname(config.DB_PATH)
    if os.path.exists(db_dir) or db_dir == '':
        print_success("Database directory exists/will be created")
    else:
        print_warning(f"Database directory does not exist: {db_dir}")
else:
    print_error("DB_PATH not found in config")

print_header("TEST 6: Stock Symbols")

if hasattr(config, 'DEFAULT_SYMBOLS'):
    symbols = config.DEFAULT_SYMBOLS
    print_info(f"Default symbols ({len(symbols)}): {', '.join(symbols)}")
    
    valid = True
    for symbol in symbols:
        if not isinstance(symbol, str) or len(symbol) < 1:
            valid = False
            print_error(f"Invalid symbol: {symbol}")
    
    if valid:
        print_success("All symbols are valid strings")
else:
    print_error("DEFAULT_SYMBOLS not found in config")

print_header("TEST 7: Validation Rules")

rules_checked = 0
if hasattr(config, 'MIN_STOCK_PRICE'):
    print_info(f"Min price: ${config.MIN_STOCK_PRICE}")
    rules_checked += 1
if hasattr(config, 'MAX_STOCK_PRICE'):
    print_info(f"Max price: ${config.MAX_STOCK_PRICE}")
    rules_checked += 1
if hasattr(config, 'MAX_NEWS_ARTICLES'):
    print_info(f"Max news articles: {config.MAX_NEWS_ARTICLES}")
    rules_checked += 1

print_success(f"Found {rules_checked} validation rules")

print_header("TEST 8: Logging Configuration")

if hasattr(config, 'LOG_FILE'):
    print_info(f"Log file: {config.LOG_FILE}")
    
    logs_dir = os.path.dirname(config.LOG_FILE)
    if os.path.exists(logs_dir):
        print_success(f"Logs directory exists: {logs_dir}")
    else:
        print_warning(f"Logs directory doesn't exist yet (will be created)")
else:
    print_error("LOG_FILE not found in config")

if hasattr(config, 'logger'):
    try:
        config.logger.info("🧪 Test log message from test_config.py")
        print_success("Logger is working")
    except Exception as e:
        print_error(f"Logger failed: {e}")
else:
    print_error("Logger not found in config")

print_header("TEST 9: Display Settings")

if hasattr(config, 'CURRENCY_SYMBOL'):
    print_info(f"Currency symbol: {config.CURRENCY_SYMBOL}")
else:
    print_warning("CURRENCY_SYMBOL not set (will use $)")

if hasattr(config, 'DATE_DISPLAY_FORMAT'):
    print_info(f"Date format: {config.DATE_DISPLAY_FORMAT}")
else:
    print_warning("DATE_DISPLAY_FORMAT not set")

print_header("📊 TEST SUMMARY")

total_tests = 10
passed_tests = 0

print_success("Configuration loaded successfully")
print_info("Check each test above for details")
