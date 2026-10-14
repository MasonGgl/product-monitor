

def analyze_products(products: list[dict]) -> dict | None:
    if not products:
        print("商品列表为空")
        return None

    max_product = max(products, key=lambda product: product["price"])
    average_price = sum(item["price"] for item in products) / len(products)
    max_sales = max(products, key=lambda product: product["sales"]*product["price"])

    return {
        "最高价格商品": max_product["name"],
        "最高价格": max_product["price"],
        "平均价格": round(average_price, 2),
        "销售额最高的商品": max_sales["name"],
        "最高销售额": (max_sales["price"]*max_sales["sales"]),
    }