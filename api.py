from fastapi import FastAPI,Query,HTTPException
from database import get_connection, init_db,get_price_drops
from crawler import fetch_all_books
from database import save_product
app = FastAPI(title="商品监控系统")

def product_to_dict(row) -> dict:
    return {
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "sales": row[3],
        "created_at": row[4],
    }

def calculate_price_change(history: list[dict]) -> float | None:
    if len(history) < 2:
        return None
    return round(history[0]["price"] - history[1]["price"],2)

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/products")
def get_products(
        limit: int = Query(default=20,ge=1, le=100),
        offset: int = Query(default=0,ge=0),
) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, price, sales, created_at
            FROM products 
            ORDER BY id DESC
            LIMIT ? offset ?
            """,
            (limit,offset),
        ).fetchall()

    return [product_to_dict(row) for row in rows]

@app.get("/products/count")
def get_products_count() -> dict:
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

    return {"count": count}

@app.get("/products/search")
def search_products(
        min_price: float = Query(default=0,ge=0),
        max_price: float = Query(default=999999,ge=0),
        limit: int = Query(default=20,ge=1, le=100),
        keyword: str = Query(default="",max_length=100),
) -> list[dict]:
    if max_price < min_price:
        raise HTTPException(
            status_code=400,
            detail="最低价不能大于最高价"
        )
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, price, sales, created_at
            FROM products 
            WHERE price BETWEEN ? AND ?
                AND name like ?
            ORDER BY price DESC
            LIMIT ?
            """,
            (min_price, max_price, f"%{keyword}%", limit),
        ).fetchall()

    return [product_to_dict(row) for row in rows]

@app.post("/crawl")
def crawl_books(
        max_pages: int = Query(default=1,ge=1, le=10)
) -> dict:
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

@app.get("/products/price-drops")
def get_price_drops_api() -> list[dict]:
    return get_price_drops()

@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            select id, name, price, sales, created_at
            FROM products 
            where id = ?
            """,
            (product_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="商品不存在"
            )
        else:
            return product_to_dict(row)

@app.get("/products/{product_id}/history")
def get_product_history(product_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT price, captured_at
            FROM products_history 
            where product_id = ?
            order by id DESC
            """,
            (product_id,),
        ).fetchall()
        return [
            {
                "price": row[0],
                "captured_at": row[1],
            }
            for row in rows
        ]

@app.get("/products/{product_id}/price_change")
def get_product_price_change(product_id: int) -> dict:
    with get_connection() as conn:
        product = conn.execute(
            "select id,name from products where id = ?",
            (product_id,),
        ).fetchone()
        if product is None:
            raise HTTPException(
                status_code=404,
                detail="商品不存在"
            )

        rows = conn.execute(
            """
            select price, captured_at
            FROM products_history 
            where product_id = ?
            order by id DESC
            limit 2""",
            (product_id,),
        ).fetchall()

        history = [{"price": row[0]} for row in rows]

        return {
            "success": True,
            "product_id": product_id,
            "name": product[1],
            "price_change": calculate_price_change(history)
        }

