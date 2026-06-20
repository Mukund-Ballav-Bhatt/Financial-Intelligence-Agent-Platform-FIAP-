import logging
import sqlite3
from contextlib import contextmanager
import os
import sys

# Add parent directory to path to find config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import DB_PATH, DB_TIMEOUT

logger = logging.getLogger(__name__)

class DatabaseBase:
    """Base class for database connections"""
    
    def __init__(self, path=None):
        """Initialize with database path"""
        if path is None:
            self.path = DB_PATH  # 👈 Use config.DB_PATH as default
        else:
            self.path = path
        logger.info(f"Database path is: {self.path}")
    
    @contextmanager
    def connect_DB(self):
        conn = None
        try:
            conn = sqlite3.connect(self.path, timeout=DB_TIMEOUT)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            logger.debug("Database connection established")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database Connection Error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Connection closed")

    def init_DB(self):
        """Initialize database with schema"""
        try:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(current_dir, 'schema.sql')
            
            logger.info(f"Loading schema from: {schema_path}")
            
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema)
                conn.commit()
                
            logger.info("Database initialized with all tables")
            return True
            
        except FileNotFoundError:
            logger.error(f"schema.sql not found at {schema_path}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error during initialization: {e}")
            return False
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    def test_connect(self):
        """Test database connection"""
        try:
            with self.connect_DB() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection Failed: {e}")
            return False