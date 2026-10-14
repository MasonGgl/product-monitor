# 商品监控系统

## 项目简介

这是一个基于 Python 的商品数据采集与查询系统，支持分页爬虫、SQLite 存储和 FastAPI 接口。

## 技术栈

- Python
- Requests
- BeautifulSoup
- SQLite
- FastAPI
- Uvicorn

## 功能

- 采集公开图书数据
- 支持多页采集
- 保存商品名称、价格、销量和采集时间
- 查询商品列表
- 按价格范围筛选
- 统计商品数量
- 通过 API 手动触发采集

## 启动方式

```bash
pip install requests beautifulsoup4 fastapi uvicorn
uvicorn api:app --reload
```

## Docker 启动

```bash
docker build -t product-monitor .
docker run --name product-monitor-app -p 8000:8000 product-monitor
```