import sys
import os
import importlib

print("=" * 70)
print("🔍 ULTIMATE DEBUG - CHECKING EVERYTHING")
print("=" * 70)

# Step 1: Check current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"\n1️⃣ Current directory: {current_dir}")

# Step 2: Check parent directory
parent_dir = os.path.dirname(current_dir)
print(f"2️⃣ Parent directory: {parent_dir}")

# Step 3: Add to path and verify
sys.path.insert(0, parent_dir)
print(f"3️⃣ Added to path: {parent_dir}")
print(f"   Python path now has: {sys.path[0]}")

# Step 4: Check if stock_fetcher_lib exists
stock_lib_path = os.path.join(parent_dir, 'stock_fetcher_lib')
print(f"\n4️⃣ Checking if stock_fetcher_lib exists at: {stock_lib_path}")
if os.path.exists(stock_lib_path):
    print(f"   ✅ FOUND: {stock_lib_path}")
    print(f"   📁 Is directory: {os.path.isdir(stock_lib_path)}")
    
    # List contents
    print(f"\n   📋 Contents of stock_fetcher_lib:")
    for file in os.listdir(stock_lib_path):
        if file.endswith('.py'):
            print(f"      • {file}")
else:
    print(f"   ❌ NOT FOUND at this location!")

# Step 5: Check __init__.py content
init_file = os.path.join(stock_lib_path, '__init__.py')
print(f"\n5️⃣ Checking __init__.py at: {init_file}")
if os.path.exists(init_file):
    print(f"   ✅ __init__.py exists")
    with open(init_file, 'r') as f:
        content = f.read()
        print(f"   📄 Content:\n{content}")
else:
    print(f"   ❌ __init__.py NOT FOUND!")

# Step 6: Check manager.py content
manager_file = os.path.join(stock_lib_path, 'manager.py')
print(f"\n6️⃣ Checking manager.py at: {manager_file}")
if os.path.exists(manager_file):
    print(f"   ✅ manager.py exists")
    with open(manager_file, 'r') as f:
        first_lines = [next(f) for _ in range(10)]  # Read first 10 lines
        print(f"   📄 First 10 lines:")
        for i, line in enumerate(first_lines, 1):
            print(f"      {i}: {line.rstrip()}")
else:
    print(f"   ❌ manager.py NOT FOUND!")

# Step 7: Try different import methods
print(f"\n7️⃣ Trying different import methods:")

# Method A: Direct import
try:
    import stock_fetcher_lib
    print(f"   ✅ Method A: import stock_fetcher_lib works")
    print(f"      Location: {stock_fetcher_lib.__file__}")
except Exception as e:
    print(f"   ❌ Method A failed: {e}")

# Method B: From import
try:
    from stock_fetcher_lib import StockFetcher
    print(f"   ✅ Method B: from stock_fetcher_lib import StockFetcher works")
except Exception as e:
    print(f"   ❌ Method B failed: {e}")

# Method C: Import manager directly
try:
    from stock_fetcher_lib.manager import StockFetcher
    print(f"   ✅ Method C: from stock_fetcher_lib.manager import StockFetcher works")
except Exception as e:
    print(f"   ❌ Method C failed: {e}")

# Method D: Import with different case
try:
    from stock_fetcher_lib import stockFetcher
    print(f"   ✅ Method D: from stock_fetcher_lib import stockFetcher works")
except Exception as e:
    print(f"   ❌ Method D failed: {e}")

# Step 8: Check if there's a typo in the file
print(f"\n8️⃣ Searching for 'stockFetcher' in manager.py:")
if os.path.exists(manager_file):
    with open(manager_file, 'r') as f:
        content = f.read()
        if 'stockFetcher' in content:
            print(f"   ❌ Found 'stockFetcher' (lowercase s) in file!")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'stockFetcher' in line:
                    print(f"      Line {i+1}: {line.strip()}")
        else:
            print(f"   ✅ No 'stockFetcher' found")
        
        if 'StockFetcher' in content:
            print(f"   ✅ Found 'StockFetcher' (capital S) in file")
        else:
            print(f"   ❌ No 'StockFetcher' found!")

print("\n" + "=" * 70)