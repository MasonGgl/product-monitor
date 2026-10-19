import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "products.db"

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                sales INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )            """
        )


def save_product(products: list[dict]) -> None:
    with get_connection() as conn:
        conn.executemany(
        """
            INSERT INTO products (name,price,sales)
            VALUES (?,?,?)
            on conflict (name) do update set 
                price = excluded.price,
                sales=excluded.sales,
                created_at=current_timestamp
            """,
            [
                (item["name"], item["price"], item["sales"])
                for item in products
            ],
        )

def count_products() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM products").fetchone()
        return row[0]