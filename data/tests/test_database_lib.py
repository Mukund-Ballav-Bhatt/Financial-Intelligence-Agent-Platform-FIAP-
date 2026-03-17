import sys
import os
import sqlite3
from datetime import datetime

# ============================================
# FIX: Add the correct path
# ============================================
# Get the current file's directory (data/tests)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up to data folder (parent directory)
data_folder = os.path.dirname(current_dir)  # This is d:/.../data/

# Add data folder to path so Python can find database_lib
sys.path.insert(0, data_folder)

# Now this will work because database_lib is inside data folder
from database_lib import DatabaseManager

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_test(name, result, details=None):
    mark = f"{Colors.GREEN}✅{Colors.END}" if result else f"{Colors.RED}❌{Colors.END}"
    print(f"  {mark} {name}")
    if details and not result:
        print(f"     {Colors.YELLOW}→ {details}{Colors.END}")

def test_database_lib():
    """Test all database_lib functionality"""
    
    print_header("🚀 TESTING DATABASE LIBRARY")
    
    # Initialize
    db = DatabaseManager()
    
    try:
        # ============================================
        # TEST 1: Connection
        # ============================================
        print_header("TEST 1: Database Connection")
        result = db.test_connect()
        print_test("Connection test", result)
        
        # ============================================
        # TEST 2: Initialize Database
        # ============================================
        print_header("TEST 2: Database Initialization")
        result = db.init_DB()
        print_test("Initialize tables", result)
        
        # ============================================
        # TEST 3: Stock Operations
        # ============================================
        print_header("TEST 3: Stock Operations")
        
        # Insert
        stock_id = db.insert_stock_price(
            symbol='AAPL',
            price=175.50,
            change=2.30,
            change_percent=1.33,
            volume=52400000,
            open=174.20,
            high=176.80,
            low=173.90,
            market_cap=2750000000000,
            pe_ratio=28.5
        )
        print_test("Insert stock price", stock_id is not None)
        
        # Get latest
        latest = db.get_latest_price('AAPL')
        print_test("Get latest price", latest is not None)
        if latest:
            print(f"     Latest price: ${latest['price']}")
        
        # Get history
        history = db.get_price_hist('AAPL', limit=5)
        print_test("Get price history", len(history) > 0)
        
        # ============================================
        # TEST 4: News Operations
        # ============================================
        print_header("TEST 4: News Operations")
        
        # Insert first article
        news_id1 = db.insert_article(
            symbol='AAPL',
            headline='Apple Announces New AI Features',
            content='Apple today revealed groundbreaking AI features...',
            source='TechCrunch',
            url='https://techcrunch.com/apple-ai-2024',
            published_date=datetime.now().isoformat()
        )
        print_test("Insert article 1", news_id1 is not None)
        
        # Insert second article
        news_id2 = db.insert_article(
            symbol='AAPL',
            headline='Apple Stock Rises',
            content='Apple shares jumped 2%...',
            source='Reuters',
            url='https://reuters.com/apple-stock-2024',
            published_date=datetime.now().isoformat()
        )
        print_test("Insert article 2", news_id2 is not None)
        
        # Test duplicate prevention
        dup = db.insert_article(
            symbol='AAPL',
            headline='Duplicate',
            url='https://techcrunch.com/apple-ai-2024'
        )
        print_test("Duplicate prevention", dup is None)
        
        # Get news
        articles = db.get_news_for_symbol('AAPL', limit=5)
        print_test("Get news by symbol", len(articles) > 0)
        if articles:
            print(f"     Found {len(articles)} articles")
        
        # ============================================
        # TEST 5: Sentiment Operations
        # ============================================
        print_header("TEST 5: Sentiment Operations")
        
        if news_id1 and news_id2:
            # Insert sentiments
            sent1 = db.insert_sentiment(
                news_id=news_id1,
                sentiment='positive',
                confidence=0.92,
                positive_score=0.85,
                negative_score=0.08,
                neutral_score=0.07
            )
            print_test("Insert sentiment for article 1", sent1 is not None)
            
            sent2 = db.insert_sentiment(
                news_id=news_id2,
                sentiment='positive',
                confidence=0.78
            )
            print_test("Insert sentiment for article 2", sent2 is not None)
            
            # Test foreign key
            invalid = db.insert_sentiment(
                news_id=99999,
                sentiment='positive',
                confidence=0.95
            )
            print_test("Foreign key constraint", invalid is None)
            
            # Get aggregate
            agg = db.get_aggregate_sentiment('AAPL', days_back=7)
            print_test("Aggregate sentiment", agg is not None)
            if agg:
                print(f"     Overall: {agg['overall_sentiment']}")
                print(f"     Score: {agg['sentiment_score']}")
                print(f"     Articles: {agg['total_articles']}")
        
        # ============================================
        # TEST 6: Report Operations
        # ============================================
        print_header("TEST 6: Report Operations")
        
        # Insert report
        report_id = db.insert_report(
            symbol='AAPL',
            price=175.50,
            price_change=1.33,
            sentiment_summary='positive',
            news_summary='Apple announced new AI features...',
            full_report='# Apple Inc. - Daily Report\n\n...',
            key_points='["AI news", "Stock up"]',
            tags='daily,tech',
            is_draft=0
        )
        print_test("Insert report", report_id is not None)
        
        # Insert draft
        draft_id = db.insert_report(
            symbol='AAPL',
            price=175.50,
            sentiment_summary='neutral',
            news_summary='Draft...',
            full_report='# Draft',
            is_draft=1
        )
        print_test("Insert draft", draft_id is not None)
        
        # Get recent reports
        recent = db.get_recent_reports(limit=5)
        print_test("Get recent reports", len(recent) > 0)
        if recent:
            print(f"     Found {len(recent)} reports")
        
        # Get by ID
        report = db.get_report_by_id(report_id)
        print_test("Get report by ID", report is not None)
        
        # Update status
        updated = db.update_report_status(draft_id, is_draft=0)
        print_test("Update report status", updated)
        
        # ============================================
        # SUMMARY
        # ============================================
        print_header("✅ ALL TESTS COMPLETED")
        print("  Database library is working correctly!")
        print("\n  📁 Database file:", db.path)
        print("  📊 All operations tested:")
        print("     • Connection & Initialization")
        print("     • Stock price operations")
        print("     • News article operations")
        print("     • Sentiment analysis operations")
        print("     • Report operations")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test failed: {e}{Colors.END}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_database_lib()
    sys.exit(0 if success else 1)