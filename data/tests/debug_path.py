import sys
import os

print("=" * 50)
print("🔍 DEBUGGING DATABASE_LIB IMPORTS")
print("=" * 50)

# Add data folder to path
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.dirname(current_dir)
sys.path.insert(0, data_folder)
print(f"📁 Added to path: {data_folder}")

try:
    # Try to import base and see what's inside
    print("\n📄 Checking base.py...")
    from database_lib import base
    print(f"   ✅ base.py imported successfully")
    
    # List all classes in base module
    classes = [cls for cls in dir(base) if not cls.startswith('__')]
    print(f"   📋 Contents of base.py: {classes}")
    
    if 'DatabaseBase' in classes:
        print(f"   ✅ DatabaseBase class found")
    else:
        print(f"   ❌ DatabaseBase NOT found in base.py")
        
except Exception as e:
    print(f"   ❌ Error importing base: {e}")

try:
    # Try to import stock_ops
    print("\n📄 Checking stock_ops.py...")
    from database_lib import stock_ops
    print(f"   ✅ stock_ops.py imported successfully")
    
    classes = [cls for cls in dir(stock_ops) if not cls.startswith('__')]
    print(f"   📋 Contents of stock_ops.py: {classes}")
    
except Exception as e:
    print(f"   ❌ Error importing stock_ops: {e}")

try:
    # Try to import manager
    print("\n📄 Checking manager.py...")
    from database_lib import manager
    print(f"   ✅ manager.py imported successfully")
    
    classes = [cls for cls in dir(manager) if not cls.startswith('__')]
    print(f"   📋 Contents of manager.py: {classes}")
    
except Exception as e:
    print(f"   ❌ Error importing manager: {e}")

try:
    # Try the full import
    print("\n📄 Trying full import from database_lib...")
    from database_lib import DatabaseManager
    print(f"   ✅ DatabaseManager imported successfully")
    
except Exception as e:
    print(f"   ❌ Error importing DatabaseManager: {e}")

print("\n" + "=" * 50)