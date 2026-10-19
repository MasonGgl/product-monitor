import sqlite3
connection = sqlite3.connect('data/products.db')
# rows = connection.execute(
#     """
#     select p1.name,p1.price
#     from products as p1
#     where p1.price = (
#         select max(p2.price)
#         from products as p2
#         where cast(p1.price as integer)/10 = cast(p2.price as integer)/10
#         )
#     order by p1.price
#     """
# ).fetchall()
# for row in rows:
#     print(row)
print(connection.execute("select count(*) from products").fetchone()[0])

connection.close()