import logging
import sqlite3
from .base import DatabaseBase

logger = logging.getLogger(__name__)

class ReportOperations(DatabaseBase):
    def insert_report(self, symbol, price, price_change=None, sentiment_summary=None,
                      news_summary=None, full_report=None, key_points=None,
                      tags=None, is_draft=0):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reports 
                    (symbol, price, price_change, sentiment_summary, 
                     news_summary, full_report, key_points, tags, is_draft)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, price, price_change, sentiment_summary,
                      news_summary, full_report, key_points, tags, is_draft))
                conn.commit()
                insert_id = cursor.lastrowid
                logger.info(f"Inserted report for {symbol} (ID: {insert_id})")
                return insert_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert report: {e}")
            return None
    
    def get_recent_reports(self, symbol=None, limit=10, include_drafts=False):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                if symbol:
                    if include_drafts:
                        cursor.execute("""
                            SELECT * FROM reports WHERE symbol = ? 
                            ORDER BY generated_date DESC LIMIT ?
                        """, (symbol, limit))
                    else:
                        cursor.execute("""
                            SELECT * FROM reports WHERE symbol = ? AND is_draft = 0
                            ORDER BY generated_date DESC LIMIT ?
                        """, (symbol, limit))
                else:
                    if include_drafts:
                        cursor.execute("SELECT * FROM reports ORDER BY generated_date DESC LIMIT ?", (limit,))
                    else:
                        cursor.execute("SELECT * FROM reports WHERE is_draft = 0 ORDER BY generated_date DESC LIMIT ?", (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get recent reports: {e}")
            return []
    
    def get_report_by_id(self, report_id):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get report {report_id}: {e}")
            return None
    
    def update_report_status(self, report_id, is_draft):
        try:
            with self.connect_DB() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE reports SET is_draft = ? WHERE id = ?", (is_draft, report_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to update report: {e}")
            return False