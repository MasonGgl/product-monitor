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


def get_price_drops() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            with ranked as (
                select 
                    product_id,
                    price,
                    ROW_NUMBER() OVER(
                        PARTITION BY product_id
                        order by id DESC
                    ) as rn
                from products_history
            )
            select 
                latest.product_id,
                latest.price   as current_price,
                previous.price as previous_price,
                round(previous.price - latest.price, 2) as drop_amount,
                p.name as name
            from ranked as latest
            join ranked as previous
              on latest.product_id = previous.product_id
                and previous.rn = 2
            join products as p
                 on (latest.product_id = p.id)
            where latest.rn = 1
              and latest.price < previous.price
            """
        ).fetchall()

        return [{
            "product_id": row[0],
            "current_price":row[1],
            "previous_price": row[2],
            "drop_amount": row[3],
            "name": row[4]
        } for row in rows]