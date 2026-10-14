import json
from pathlib import Path

from analyzer import analyze_products
from crawler import fetch_all_books
from database import init_db,save_product,count_products


def main() -> None:
    init_db()
    products = fetch_all_books("https://books.toscrape.com", max_page=3)

    if not products:
        print("没有采集到商品数据，程序结束")
        return

    save_product(products)
    print(f"本次保存 {len(products)} 条商品")
    print(f"数据库共有 {count_products()} 条商品")

    result = analyze_products(products)

    output_path = Path(__file__).parent / "result.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"分析完成，结果已保存到：{output_path}")

if __name__ == "__main__":
    main()