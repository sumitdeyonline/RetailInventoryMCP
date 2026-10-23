import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "inventory.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_stock_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve stock information for a specific product ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def search_products(query: str) -> List[Dict[str, Any]]:
    """Search for products by name or category."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT * FROM products 
        WHERE name LIKE ? OR category LIKE ?
    """, (search_term, search_term))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
