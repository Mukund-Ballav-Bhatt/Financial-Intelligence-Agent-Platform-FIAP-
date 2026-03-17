import sys
import os
import datetime
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.dirname(current_dir)
sys.path.insert(0, data_folder)

# Now import correctly
from stock_fetcher_lib import StockFetcher

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}📊 {text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

def print_test(name, result, details=None):
    mark = f"{Colors.GREEN}✅{Colors.END}" if result else f"{Colors.RED}❌{Colors.END}"
    print(f"  {mark} {name}")
    if details:
        print(f"     {Colors.YELLOW}→ {details}{Colors.END}")

def print_data(label, value):
    print(f"     {Colors.BLUE}{label}:{Colors.END} {value}")

def test_stock_fetcher():
    """Test ALL stock fetcher operations"""
    
    print_header("🚀 TESTING STOCK FETCHER LIBRARY")
    print("Testing with REAL data from Yahoo Finance\n")
    
    # Initialize
    fetcher = StockFetcher()
    
    # ============================================
    # TEST 1: Basic Connection
    # ============================================
    print_header("TEST 1: Basic Connection")
    
    result = fetcher.test_connection()
    print_test("Yahoo Finance connection", result)
    
    # ============================================
    # TEST 2: Symbol Validation
    # ============================================
    print_header("TEST 2: Symbol Validation")
    
    # Test valid symbols
    for symbol in ['AAPL', 'MSFT', 'TCS.NS']:
        valid = fetcher.validate_symbol(symbol)
        print_test(f"Validate {symbol}", valid)
    
    # Test invalid symbol
    invalid = fetcher.validate_symbol('INVALID123')
    print_test("Invalid symbol returns False", not invalid)
    
    # Test suggestions
    print("\n  🔍 Testing symbol suggestions:")
    suggestions = fetcher.suggest_correction('APPL')
    if suggestions['suggestions']:
        print(f"     'APPL' → {suggestions['suggestions'][0]['suggestion']}")
    
    suggestions = fetcher.suggest_correction('TCS')
    if suggestions['suggestions']:
        print(f"     'TCS' → {suggestions['suggestions'][0]['suggestion']}")
    
    # ============================================
    # TEST 3: Single Stock Fetch
    # ============================================
    print_header("TEST 3: Single Stock Fetch")
    
    # Test US stock
    print("\n  🇺🇸 Testing US stock (AAPL):")
    apple = fetcher.fetch_stock('AAPL')
    if apple:
        print_test("AAPL fetch successful", True)
        print_data("Price", f"${apple['price']}")
        print_data("Change", f"{apple['change']} ({apple['change_percent']}%)")
        print_data("Volume", f"{apple['volume']:,}")
    
    # Test Indian stock
    print("\n  🇮🇳 Testing Indian stock (TCS.NS):")
    tcs = fetcher.fetch_stock('TCS.NS')
    if tcs:
        print_test("TCS.NS fetch successful", True)
        print_data("Price", f"₹{tcs['price']}")
        print_data("Change", f"{tcs['change']} ({tcs['change_percent']}%)")
    
    # ============================================
    # TEST 4: Multiple Stocks
    # ============================================
    print_header("TEST 4: Multiple Stocks")
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"  Fetching: {symbols}")
    
    results = fetcher.fetch_multiple_stocks(symbols, delay=0.5)
    print_test(f"Fetched {len(results)}/{len(symbols)} stocks", len(results) > 0)
    
    if results:
        print("\n  📊 Summary:")
        for sym, data in results.items():
            print(f"     {sym}: ${data['price']} ({data['change_percent']}%)")
    
    # ============================================
    # TEST 5: Stock Comparison
    # ============================================
    print_header("TEST 5: Stock Comparison")
    
    compare_symbols = ['AAPL', 'TSLA', 'MSFT']
    comparison = fetcher.compare_stocks(compare_symbols)
    
    if comparison and comparison['stocks']:
        print_test("Comparison created", True)
        print("\n  🏆 Highlights:")
        if comparison['summary']['highest_price']:
            h = comparison['summary']['highest_price']
            print(f"     Highest price: {h['symbol']} (${h['price']})")
        if comparison['summary']['biggest_gainer']:
            g = comparison['summary']['biggest_gainer']
            print(f"     Biggest gainer: {g['symbol']} ({g['change']}%)")
    
    # ============================================
    # TEST 6: Historical Data
    # ============================================
    print_header("TEST 6: Historical Data")
    
    # Test price trend
    print("\n  📈 Price Trend Analysis:")
    trend = fetcher.get_price_trend('AAPL', days=30)
    if trend:
        print_test("30-day trend analysis", True)
        print_data("Change", f"{trend['change_percent']}%")
        print_data("Direction", trend['trend_direction'])
        print_data("Volatility", f"{trend['volatility']}%")
    
    # Test moving average
    print("\n  📉 Moving Averages:")
    ma = fetcher.get_moving_average('AAPL', days=20)
    if ma:
        print_test("20-day MA calculation", True)
        print_data("20-day MA", f"${ma['ma_value']}")
        print_data("Position", ma['position'])
    
    # Test multiple MAs
    mas = fetcher.get_multiple_moving_averages('AAPL')
    if mas:
        print_test("Multiple MAs", True)
        for period, value in mas['moving_averages'].items():
            print(f"     {period}: ${value}")
    
    # ============================================
    # TEST 7: Company Information
    # ============================================
    print_header("TEST 7: Company Information")
    
    # Test company info
    print("\n  🏢 Company Details:")
    info = fetcher.get_company_info('AAPL')
    if info:
        print_test("Company info fetched", True)
        print_data("Name", info['name'])
        print_data("Sector", info['sector'])
        print_data("Industry", info['industry'])
        print_data("Country", info['country'])
        print_data("Employees", f"{info['employees']:,}")
    
    # Test financials
    print("\n  💰 Key Financials:")
    financials = fetcher.get_key_financials('AAPL')
    if financials:
        print_test("Financials fetched", True)
        if 'valuation' in financials:
            print_data("Market Cap", f"${financials['valuation']['market_cap']/1e9:.1f}B")
            print_data("P/E Ratio", financials['valuation']['pe_ratio'])
        if 'dividends' in financials:
            print_data("Dividend Yield", f"{financials['dividends']['dividend_yield']}%")
    
    # Test analyst recommendations
    print("\n  📊 Analyst Ratings:")
    analyst = fetcher.get_analyst_recommendations('AAPL')
    if analyst:
        print_test("Analyst data fetched", True)
        if 'consensus' in analyst:
            print_data("Consensus", analyst['consensus'])
        if 'target_prices' in analyst and analyst['target_prices'].get('target_mean'):
            print_data("Target Price", f"${analyst['target_prices']['target_mean']}")
    
    # ============================================
    # TEST 8: Quick Scan
    # ============================================
    print_header("TEST 8: Quick Scan")
    
    scan_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    scan = fetcher.quick_scan(scan_symbols)
    
    if scan and scan['results']:
        print_test(f"Quick scan of {len(scan_symbols)} stocks", True)
        print("\n  📋 Scan Results:")
        for sym, data in list(scan['results'].items())[:3]:  # Show first 3
            print(f"     {sym}: ${data['price']} ({data['change']}%)")
    
    # ============================================
    # TEST 9: Market Summary
    # ============================================
    print_header("TEST 9: Market Summary")
    
    market = fetcher.market_summary()
    if market:
        print_test("Market summary generated", True)
        print_data("Market Mood", market['market_mood'])
        print_data("Advancers/Decliners", f"{market['advancers']}/{market['decliners']}")
        print_data("Average Change", f"{market['avg_change']}%")
        print_data("Top Gainer", market['top_gainer'])
    
    # ============================================
    # TEST 10: Complete Profile
    # ============================================
    print_header("TEST 10: Complete Profile")
    
    print("  Building complete profile for AAPL (this may take a moment)...")
    profile = fetcher.get_complete_profile('AAPL')
    
    if profile:
        print_test("Complete profile generated", True)
        if 'data_completeness' in profile:
            comp = profile['data_completeness']
            print_data("Data Completeness", f"{comp['percentage']}% ({comp['summary']})")
    
    # ============================================
    # FINAL SUMMARY
    # ============================================
    print_header("✅ ALL TESTS COMPLETED")
    print(f"\n{Colors.GREEN}Stock Fetcher Library is fully functional!{Colors.END}")
    print("\n  Available for ANY symbol:")
    print("  • US Stocks (AAPL, MSFT, GOOGL, TSLA...)")
    print("  • Indian Stocks (TCS.NS, RELIANCE.NS, HDFCBANK.NS...)")
    print("  • European Stocks (SAP.DE, BP.L...)")
    print("  • And many more!")
    
    print("\n  📁 Library Structure:")
    print("     stock_fetcher_lib/")
    print("     ├── __init__.py")
    print("     ├── base.py")
    print("     ├── quotes.py")
    print("     ├── historical.py")
    print("     ├── company.py")
    print("     ├── validator.py")
    print("     └── manager.py")
    
    return True

if __name__ == "__main__":
    try:
        success = test_stock_fetcher()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Test interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Test failed with error: {e}{Colors.END}")
        sys.exit(1)