import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "products.db"

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

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

        conn.execute(
            """
            create table if not exists products_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER not null,
                price REAL NOT NULL,
                captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            """
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
        for item in products:
            row = conn.execute(
                "select id from products where name= ? ",
                (item["name"],),
            ).fetchone()

            conn.execute(
                """
                insert into products_history (product_id,price)
                values (?,?)
                """,
                (row[0], item["price"]),
            )

def count_products() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM products").fetchone()
        return row[0]