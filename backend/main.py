# ===== 修复版 main.py（客户下拉 + 数据库统一） =====
import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import sqlite3
from datetime import datetime

app = FastAPI(title="物流管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 关键：使用旧数据库
DB_FILE = "data.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


# 客户接口（修复）
@app.get("/api/customers")
async def get_customers(search: str = Query(None)):
    conn = get_db()
    cursor = conn.cursor()

    result = []

    # 客户表
    if search:
        cursor.execute(
            "SELECT customer_name, company_name FROM customers WHERE customer_name LIKE ? OR company_name LIKE ?",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute("SELECT customer_name, company_name FROM customers")

    rows = cursor.fetchall()

    for row in rows:
        name = row["customer_name"] or row["company_name"]
        if name:
            result.append({
                "value": name,
                "customer_name": name
            })

    # 订单兜底
    if not result:
        cursor.execute(
            "SELECT DISTINCT customer_name FROM orders WHERE customer_name IS NOT NULL AND TRIM(customer_name) <> ''"
        )
        rows = cursor.fetchall()

        for row in rows:
            name = row["customer_name"]
            if name:
                result.append({
                    "value": name,
                    "customer_name": name
                })

    conn.close()
    return result


@app.get("/")
async def root():
    return {"status": "ok"}


if __name__ == "__main__":
    print("后端启动：http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
