from fastapi import FastAPI
from database import get_connection, init_db
from crawler import fetch_all_books
from database import save_product
app = FastAPI(title="商品监控系统")

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/products")
def get_products(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, price, sales, created_at
            FROM products 
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "sales": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]

@app.get("/products/count")
def get_products_count() -> dict:
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchall()[0]

    return {"count": count}

@app.get("/products/sreach")
def search_products(
        min_price: float = 0,
        max_price: float = 999999,
        limit: int = 20,
) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, price, sales, created_at
            FROM products 
            WHERE price BETWEEN ? AND ?
            ORDER BY price DESC
            LIMIT ?
            """,
            (min_price, max_price, limit),
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "sales": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]

@app.post("/crawl")
def crawl_books(max_pages: int = 1) -> dict:
    products = fetch_all_books(
        "https://books.toscrape.com/",
        max_page=max_pages,
    )
    if not products:
        return {
            "success": False,
            "message":"没有采集到商品",
            "count": 0,
        }
    save_product(products)
    return {
        "success": True,
        "message":"采集并保存成功",
        "count": len(products),
    }