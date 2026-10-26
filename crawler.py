import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_books(url:str) -> tuple[list[dict], str | None, bool]:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
                                )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败：{e}")
        return [], None, False

    soup = BeautifulSoup(response.content, "html.parser")
    products = []

    for item in soup.select("article.product_pod"):
        name_node = item.select_one("h3 a")
        price_text_node = item.select_one("div.product_price p.price_color")
        if name_node is None or price_text_node is None:
            continue
        name = name_node["title"]
        price_text = price_text_node.get_text(strip=True)
        price = float(price_text.replace("£", ""))
        products.append({"name": name, "price": price, "sales": 1})

    next_node = soup.select_one("ul.pager li.next a")
    next_url = None
    if next_node is not None:
        next_url = urljoin(url, next_node["href"])

    return products, next_url, True

def fetch_all_books(start_url:str, max_page: int = 3) -> tuple[list[dict], int, int | None]:
    all_products = []
    current_url = start_url
    successful_page = 0
    failed_page = None

    for page_number in range(1, max_page + 1):
        products, next_url, net_status = fetch_books(current_url)
        if not net_status:
            print(f"第{page_number}页请求失败")
            failed_page = page_number
            break
        all_products.extend(products)

        print(f"第 {page_number} 页采集 {len(products)} 条")
        successful_page += 1

        if next_url is None:
            break

        current_url = next_url
    return all_products,successful_page,failed_page


if __name__=="__main__":
    books,success_page,failed_page = fetch_all_books("https://books.toscrape.com/", 6)
    print(f"成功采集 {success_page} 页，共 {len(books)} 本书")
    print(f"失败页：{failed_page}")
    print(books[:3])