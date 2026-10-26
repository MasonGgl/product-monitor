import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("""
    create table if not exists products 
    (
        id integer primary key,
        name text not null
    )
""")
conn.execute("""
    create table if not exists products_history 
    (
        id integer primary key autoincrement,
        product_id integer not null,
        price REAL
    )
""")
conn.execute(
    """
    insert into products(id,name) values (?,?)
    """,(1,'测试书'),
)

conn.executemany(
    """
    insert into products_history (product_id, price) values (?, ?)
    """,
    [(1,30),(1,25)],
)

rows = conn.execute(
    """
    with ranked as (
        select product_id,
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
    join products as p on p.id = latest.product_id
    where latest.rn = 1
      and latest.price < previous.price        
    """
).fetchall()

for product_id, current_price, previous_price,drop_amount,name in rows:
    print({
        "product_id": product_id,
        "current_price": current_price,
        "previous_price": previous_price,
        "drop_amount": drop_amount,
        "name": name,
    })

conn.close()