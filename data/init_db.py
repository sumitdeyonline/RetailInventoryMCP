import csv
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "inventory.csv")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            stock_quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            cost_price REAL NOT NULL,
            sales_last_30d INTEGER NOT NULL,
            seasonality_index REAL NOT NULL,
            competitor_price_avg REAL NOT NULL
        )
    """)

    # Clear existing data just in case
    cursor.execute("DELETE FROM products")

    # Insert data from CSV
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO products (id, name, category, stock_quantity, price, cost_price, sales_last_30d, seasonality_index, competitor_price_avg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['id'],
                row['name'],
                row['category'],
                int(row['stock_quantity']),
                float(row['price']),
                float(row['cost_price']),
                int(row['sales_last_30d']),
                float(row['seasonality_index']),
                float(row['competitor_price_avg'])
            ))

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_db()
