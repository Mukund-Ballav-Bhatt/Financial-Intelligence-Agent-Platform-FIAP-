"""
Test script for database schema
Tests all tables and relationships
"""
import sqlite3
import os
import sys
from datetime import datetime

# Add colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, result, error=None):
    """Print test result with color"""
    if result:
        print(f"{Colors.GREEN}✅ PASS: {name}{Colors.END}")
    else:
        print(f"{Colors.RED}❌ FAIL: {name}{Colors.END}")
        if error:
            print(f"   Error: {error}")

def run_test():
    """Run all schema tests"""
    
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}🔧 TESTING DATABASE SCHEMA{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")
    
   #Use a test database file(so we don't affect real data)
    db_path = 'test_financial.db'
    print(f"\n📁 Using test database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()                      # TEST 1: Read and execute schema   
        print(f"\n{Colors.BLUE}📝 TEST 1: Loading Schema{Colors.END}")
        
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
            conn.commit()
            print_test("Schema loaded successfully", True)
        
        # TEST 2: Check all tables exist
        print(f"\n{Colors.BLUE}📊 TEST 2: Table Existence{Colors.END}")
        
        expected_tables = [
            'stock_prices',
            'news_articles', 
            'sentiment_analysis',
            'reports'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            exists = table in existing_tables
            print_test(f"Table '{table}' exists", exists)
        
        # TEST 3: Insert test data
        print(f"\n{Colors.BLUE}📝 TEST 3: Insert Test Data{Colors.END}")
        
        # Insert stock price
        cursor.execute("""
            INSERT INTO stock_prices (symbol, price, change, volume)
            VALUES (?, ?, ?, ?)
        """, ('AAPL', 175.50, 2.30, 50000000))
        stock_id = cursor.lastrowid
        print_test("Insert stock price", stock_id > 0)
        
        # Insert news article
        cursor.execute("""
            INSERT INTO news_articles (symbol, headline, content, url, published_date)
            VALUES (?, ?, ?, ?, ?)
        """, ('AAPL', 'Test Headline', 'Test Content', 
              'http://test.com/article1', datetime.now().isoformat()))
        news_id = cursor.lastrowid
        print_test("Insert news article", news_id > 0)
        
        # Insert sentiment
        cursor.execute("""
            INSERT INTO sentiment_analysis (news_id, sentiment, confidence)
            VALUES (?, ?, ?)
        """, (news_id, 'positive', 0.95))
        sentiment_id = cursor.lastrowid
        print_test("Insert sentiment analysis", sentiment_id > 0)
        
        # Insert report
        cursor.execute("""
            INSERT INTO reports (symbol, price, sentiment_summary, full_report)
            VALUES (?, ?, ?, ?)
        """, ('AAPL', 175.50, 'positive', 'Test report content'))
        report_id = cursor.lastrowid
        print_test("Insert report", report_id > 0)
        
        conn.commit()
        
        # TEST 4: Foreign Key Constraint
        print(f"\n{Colors.BLUE}🔗 TEST 4: Foreign Key Constraint{Colors.END}")
        
        try:
            # Try to insert sentiment with invalid news_id
            cursor.execute("""
                INSERT INTO sentiment_analysis (news_id, sentiment, confidence)
                VALUES (99999, 'positive', 0.95)
            """)
            conn.commit()
            print_test("Foreign key should reject invalid news_id", False)
        except sqlite3.IntegrityError as e:
            print_test("Foreign key constraint working", True, str(e))
        
        # TEST 5: Check Constraints
        print(f"\n{Colors.BLUE}✅ TEST 5: Check Constraints{Colors.END}")
        
        # Test sentiment CHECK constraint
        try:
            cursor.execute("""
                INSERT INTO sentiment_analysis (news_id, sentiment, confidence)
                VALUES (?, ?, ?)
            """, (news_id, 'invalid_sentiment', 0.95))
            conn.commit()
            print_test("Sentiment CHECK constraint", False)
        except sqlite3.IntegrityError:
            print_test("Sentiment CHECK constraint working", True)
        
        # Test confidence CHECK constraint
        try:
            cursor.execute("""
                INSERT INTO sentiment_analysis (news_id, sentiment, confidence)
                VALUES (?, ?, ?)
            """, (news_id, 'positive', 2.5))
            conn.commit()
            print_test("Confidence CHECK constraint", False)
        except sqlite3.IntegrityError:
            print_test("Confidence CHECK constraint working", True)
        
        # TEST 6: Retrieve and verify data
        print(f"\n{Colors.BLUE}🔍 TEST 6: Data Retrieval{Colors.END}")
        
        # Get stock price
        cursor.execute("SELECT * FROM stock_prices WHERE symbol='AAPL' ORDER BY timestamp DESC LIMIT 1")
        stock = cursor.fetchone()
        print_test("Retrieve stock price", stock is not None)
        if stock:
            print(f"   Latest AAPL price: ${stock[2]}")
        
        # Get news with sentiment
        cursor.execute("""
            SELECT n.headline, s.sentiment, s.confidence
            FROM news_articles n
            JOIN sentiment_analysis s ON n.id = s.news_id
            WHERE n.symbol='AAPL'
        """)
        result = cursor.fetchone()
        print_test("Join news with sentiment", result is not None)
        if result:
            print(f"   News: {result[0][:50]}...")
            print(f"   Sentiment: {result[1]} ({result[2]})")
        
        # TEST 7: Check indexes exist
        print(f"\n{Colors.BLUE}📇 TEST 7: Indexes{Colors.END}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        
        expected_indexes = [
            'idx_stock_symbol',
            'idx_news_symbol',
            'idx_reports_symbol'
        ]
        
        for idx in expected_indexes:
            exists = idx in indexes
            print_test(f"Index '{idx}' exists", exists)
        
        print(f"   Total indexes created: {len(indexes)}")
        
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
        print(f"{Colors.GREEN}✅ SCHEMA TESTS COMPLETE!{Colors.END}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.END}")
        
        # Clean up
        conn.close()
        
        # Ask if user wants to keep test database
        response = input(f"\n{Colors.YELLOW}Delete test database? (y/n): {Colors.END}")
        if response.lower() == 'y':
            os.remove(db_path)
            print("Test database deleted")
        else:
            print(f"Test database kept: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Test failed with error: {e}{Colors.END}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)           # Checking if above code run Completely