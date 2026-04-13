import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from urllib.parse import quote
from typing import Optional
import uvicorn
import sqlite3
import json
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib.units import cm

app = FastAPI(title="物流管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "data.db"

def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL, role TEXT DEFAULT 'operator', real_name TEXT, created_at TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, order_no TEXT, channel TEXT,
        warehouse TEXT DEFAULT '铁士', boxes INTEGER DEFAULT 0, total_weight REAL DEFAULT 0.0,
        cbm REAL DEFAULT 0.0, warehouse_code TEXT, receiver_name TEXT, address1 TEXT,
        address2 TEXT, city TEXT, state TEXT, zip_code TEXT, phone TEXT, phone2 TEXT,
        is_customs INTEGER DEFAULT 0, kg_price REAL, business_no TEXT, vessel_voyage TEXT,
        volume_price REAL, volume_ratio REAL, product_name TEXT, fba_no TEXT,
        is_non_standard INTEGER DEFAULT 0, delivery_requirement TEXT, expected_arrival TEXT,
        warehouse_note TEXT, order_note TEXT, generate_bill INTEGER DEFAULT 0,
        status TEXT DEFAULT '待入库', created_at TEXT, updated_at TEXT, created_by TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT UNIQUE, tax_no TEXT,
        company_name TEXT, bank_account TEXT, finance_contact TEXT, finance_phone TEXT, created_at TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS business_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT, business_no TEXT UNIQUE NOT NULL,
        business_type TEXT NOT NULL, business_type_name TEXT, container_no TEXT,
        container_type TEXT, bill_no TEXT, ship_name TEXT, voyage TEXT, remark TEXT,
        create_date TEXT, status TEXT DEFAULT '正常', created_by TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS operation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT NOT NULL, record_id INTEGER,
        operation_type TEXT NOT NULL, operator TEXT NOT NULL, operator_role TEXT,
        old_data TEXT, new_data TEXT, reason TEXT, operated_at TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT, order_no TEXT, boxes INTEGER, box_no TEXT,
        status TEXT DEFAULT '在库', inbound_date TEXT, weight REAL,
        length REAL, width REAL, height REAL, volume REAL, volume_weight REAL,
        amazon_warehouse TEXT, non_std_weight REAL, non_std_size TEXT,
        zip_code TEXT, delivery_method TEXT, ups_tracking TEXT,
        ups_scan_time TEXT, sign_time TEXT, ups_master_no TEXT,
        channel TEXT, business_no TEXT, business_type TEXT,
        ship_name TEXT, voyage TEXT, remark TEXT,
        created_at TEXT, updated_at TEXT)""")
    
    default_users = [('admin', '123456', 'admin', '超级管理员')]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for u in default_users:
        try:
            cursor.execute("INSERT INTO users (username, password, role, real_name, created_at) VALUES (?, ?, ?, ?, ?)", (*u, now))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

init_db()

@app.get("/")
async def read_root():
    return {"message": "OK", "status": "running"}

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", 
                      (data.get("username"), data.get("password")))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"success": True, "user": dict(user)}
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 用户管理 =================
@app.get("/api/users")
async def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, real_name, created_at FROM users ORDER BY id")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/users")
async def create_user(request: Request):
    try:
        data = await request.json()
        if not data.get("username") or not data.get("password"):
            raise HTTPException(status_code=400, detail="用户名和密码不能为空")
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (username, password, role, real_name, created_at) VALUES (?, ?, ?, ?, ?)",
                      (data["username"], data["password"], data.get("role", "operator"), data.get("real_name", ""), now))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"用户 {data['username']} 创建成功"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="用户名已存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        if data.get("password"):
            cursor.execute("UPDATE users SET password=?, role=?, real_name=? WHERE id=?",
                          (data["password"], data["role"], data["real_name"], user_id))
        else:
            cursor.execute("UPDATE users SET role=?, real_name=? WHERE id=?",
                          (data["role"], data["real_name"], user_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "用户信息更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "用户已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 操作日志 =================
@app.get("/api/operation-logs")
async def get_operation_logs(table_name: str = Query(None), operator: str = Query(None),
                             operation_type: str = Query(None), start_date: str = Query(None),
                             end_date: str = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    sql, params = "SELECT * FROM operation_logs WHERE 1=1", []
    if table_name:
        sql += " AND table_name = ?"
        params.append(table_name)
    if operator:
        sql += " AND operator LIKE ?"
        params.append(f"%{operator}%")
    if operation_type:
        sql += " AND operation_type = ?"
        params.append(operation_type)
    if start_date:
        sql += " AND operated_at >= ?"
        params.append(start_date)
    if end_date:
        sql += " AND operated_at <= ?"
        params.append(end_date)
    sql += " ORDER BY operated_at DESC LIMIT 200"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    logs = []
    for row in rows:
        log = dict(row)
        try:
            log['old_data'] = json.loads(log['old_data']) if log['old_data'] else None
        except:
            pass
        try:
            log['new_data'] = json.loads(log['new_data']) if log['new_data'] else None
        except:
            pass
        logs.append(log)
    conn.close()
    return logs

# ================= 在库管理 =================
@app.get("/api/inventory")
async def get_inventory(
    customer_id: Optional[str] = Query(None),
    order_no: Optional[str] = Query(None),
    box_no: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    amazon_warehouse: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    business_no: Optional[str] = Query(None),
    business_type: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None),
    ups_tracking: Optional[str] = Query(None)
):
    conn = get_db()
    cursor = conn.cursor()
    sql_parts = ["SELECT * FROM inventory WHERE 1=1"]
    params = []
    
    def add_multi_search(field, value):
        if value:
            values = [v.strip() for v in value.split() if v.strip()]
            if len(values) > 1:
                clauses = " OR ".join([f"{field} LIKE ?" for _ in values])
                sql_parts.append(f" AND ({clauses})")
                params.extend([f"%{v}%" for v in values])
            elif values:
                sql_parts.append(f" AND {field} LIKE ?")
                params.append(f"%{values[0]}%")
    
    add_multi_search("customer_id", customer_id)
    add_multi_search("order_no", order_no)
    add_multi_search("box_no", box_no)
    add_multi_search("status", status)
    add_multi_search("amazon_warehouse", amazon_warehouse)
    add_multi_search("channel", channel)
    add_multi_search("business_no", business_no)
    add_multi_search("business_type", business_type)
    add_multi_search("zip_code", zip_code)
    add_multi_search("ups_tracking", ups_tracking)
    
    sql_parts.append(" ORDER BY id DESC")
    cursor.execute(" ".join(sql_parts), params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/inventory")
async def create_inventory(request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        l = float(data.get('length', 0) or 0)
        w = float(data.get('width', 0) or 0)
        h = float(data.get('height', 0) or 0)
        volume = (l * w * h) / 1000000 if all([l, w, h]) else 0
        volume_weight = (l * w * h) / 6000 if all([l, w, h]) else 0
        
        cursor.execute("""INSERT INTO inventory (
            customer_id, order_no, boxes, box_no, status, inbound_date, weight,
            length, width, height, volume, volume_weight,
            amazon_warehouse, non_std_weight, non_std_size,
            zip_code, delivery_method, ups_tracking,
            ups_scan_time, sign_time, ups_master_no,
            channel, business_no, business_type,
            ship_name, voyage, remark, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.get('customer_id'), data.get('order_no'), data.get('boxes', 0), data.get('box_no'),
             data.get('status', '在库'), data.get('inbound_date'), data.get('weight', 0),
             l, w, h, volume, volume_weight,
             data.get('amazon_warehouse'), data.get('non_std_weight', 0), data.get('non_std_size'),
             data.get('zip_code'), data.get('delivery_method'), data.get('ups_tracking'),
             data.get('ups_scan_time'), data.get('sign_time'), data.get('ups_master_no'),
             data.get('channel'), data.get('business_no'), data.get('business_type'),
             data.get('ship_name'), data.get('voyage'), data.get('remark'), now, now))
        conn.commit()
        conn.close()
        return {"success": True, "message": "记录创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/inventory/{item_id}")
async def update_inventory(item_id: int, request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        l = float(data.get('length', 0) or 0)
        w = float(data.get('width', 0) or 0)
        h = float(data.get('height', 0) or 0)
        volume = (l * w * h) / 1000000 if all([l, w, h]) else 0
        volume_weight = (l * w * h) / 6000 if all([l, w, h]) else 0
        
        cursor.execute("""UPDATE inventory SET
            customer_id=?, order_no=?, boxes=?, box_no=?, status=?, inbound_date=?, weight=?,
            length=?, width=?, height=?, volume=?, volume_weight=?,
            amazon_warehouse=?, non_std_weight=?, non_std_size=?,
            zip_code=?, delivery_method=?, ups_tracking=?,
            ups_scan_time=?, sign_time=?, ups_master_no=?,
            channel=?, business_no=?, business_type=?,
            ship_name=?, voyage=?, remark=?, updated_at=? WHERE id=?""",
            (data.get('customer_id'), data.get('order_no'), data.get('boxes'), data.get('box_no'),
             data.get('status'), data.get('inbound_date'), data.get('weight'),
             l, w, h, volume, volume_weight,
             data.get('amazon_warehouse'), data.get('non_std_weight'), data.get('non_std_size'),
             data.get('zip_code'), data.get('delivery_method'), data.get('ups_tracking'),
             data.get('ups_scan_time'), data.get('sign_time'), data.get('ups_master_no'),
             data.get('channel'), data.get('business_no'), data.get('business_type'),
             data.get('ship_name'), data.get('voyage'), data.get('remark'), now, item_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/inventory/{item_id}")
async def delete_inventory(item_id: int, request: Request):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 业务管理 =================
@app.get("/api/business")
async def get_business(business_no: str = Query(None), container_no: str = Query(None),
                       bill_no: str = Query(None), business_type: str = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    sql, params = "SELECT * FROM business_info WHERE 1=1", []
    if business_no:
        sql += " AND business_no LIKE ?"
        params.append(f"%{business_no}%")
    if container_no:
        sql += " AND container_no LIKE ?"
        params.append(f"%{container_no}%")
    if bill_no:
        sql += " AND bill_no LIKE ?"
        params.append(f"%{bill_no}%")
    if business_type:
        sql += " AND business_type = ?"
        params.append(business_type)
    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/business")
async def create_business(request: Request):
    try:
        data = await request.json()
        if not data.get("business_type"):
            raise HTTPException(status_code=400, detail="请选择业务类型")
        now = datetime.now()
        year_month = now.strftime("%Y%m")
        prefix = f"YL{year_month}"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT business_no FROM business_info WHERE business_no LIKE ? ORDER BY business_no DESC LIMIT 1", (f"{prefix}%",))
        last_record = cursor.fetchone()
        if last_record:
            last_no = last_record['business_no']
            try:
                seq = int(last_no[len(prefix):len(prefix)+3]) + 1
            except:
                seq = 1
        else:
            seq = 1
        new_business_no = f"{prefix}{seq:03d}-{data['business_type']}"
        type_map = {'601':'代操作','602':'美国海运-美森','603':'美国海运尾程','604':'美国空运','605':'美国空运尾程','606':'日本海运','607':'日本空运','608':'转同行','609':'账单用','610':'美国海运-普船','611':'加拿大空海运','612':'东南亚空海运'}
        cursor.execute("""INSERT INTO business_info (business_no, business_type, business_type_name, container_no, container_type, bill_no, ship_name, voyage, remark, create_date, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (new_business_no, data["business_type"], type_map.get(data["business_type"], ""), data.get("container_no", ""), data.get("container_type", ""), data.get("bill_no", ""), data.get("ship_name", ""), data.get("voyage", ""), data.get("remark", ""), now.strftime("%Y-%m-%d"), "正常", data.get("created_by", "system")))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"业务创建成功，编号：{new_business_no}"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="业务编号已存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/business/{business_id}")
async def update_business(business_id: int, request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""UPDATE business_info SET container_no=?, container_type=?, bill_no=?, ship_name=?, voyage=?, remark=?, status=? WHERE id=?""",
            (data.get("container_no"), data.get("container_type"), data.get("bill_no"), data.get("ship_name"), data.get("voyage"), data.get("remark"), data.get("status", "正常"), business_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "业务信息更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/business/{business_id}")
async def delete_business(business_id: int, request: Request):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM business_info WHERE id=?", (business_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "业务信息已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 订单管理 =================
@app.get("/api/orders")
async def get_orders(
    order_no: Optional[str] = Query(None),
    customer_name: Optional[str] = Query(None),
    warehouse: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    business_no: Optional[str] = Query(None),
    fba_no: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    conn = get_db()
    cursor = conn.cursor()
    sql_parts = ["SELECT * FROM orders WHERE 1=1"]
    params = []
    if order_no:
        nos = [n.strip() for n in order_no.split() if n.strip()]
        if len(nos) > 1:
            sql_parts.append(f" AND ({' OR '.join(['order_no LIKE ?'] * len(nos))})")
            params.extend([f"%{n}%" for n in nos])
        elif nos:
            sql_parts.append(" AND order_no LIKE ?")
            params.append(f"%{nos[0]}%")
    if customer_name:
        sql_parts.append(" AND customer_name LIKE ?")
        params.append(f"%{customer_name}%")
    if business_no:
        bnos = [b.strip() for b in business_no.split() if b.strip()]
        if len(bnos) > 1:
            sql_parts.append(f" AND ({' OR '.join(['business_no LIKE ?'] * len(bnos))})")
            params.extend([f"%{b}%" for b in bnos])
        elif bnos:
            sql_parts.append(" AND business_no LIKE ?")
            params.append(f"%{bnos[0]}%")
    if fba_no:
        sql_parts.append(" AND fba_no LIKE ?")
        params.append(f"%{fba_no}%")
    if warehouse:
        sql_parts.append(" AND warehouse = ?")
        params.append(warehouse)
    if channel:
        sql_parts.append(" AND channel = ?")
        params.append(channel)
    if status:
        sql_parts.append(" AND status = ?")
        params.append(status)
    sql_parts.append(" ORDER BY id DESC")
    cursor.execute(" ".join(sql_parts), params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/orders/{order_id}")
async def get_order_detail(order_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return dict(order)

@app.post("/api/orders")
async def create_order(request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_no = (data.get("order_no") or "").strip()
        if not order_no:
            customer_name = (data.get("customer_name") or "").strip()
            customer_code = ""
            if customer_name:
                cursor.execute("SELECT customer_name FROM customers WHERE customer_name LIKE ? LIMIT 1", (f"%{customer_name}%",))
                row = cursor.fetchone()
                if row:
                    full = row['customer_name']
                    customer_code = full.split(' - ')[0].strip() if ' - ' in full else (full.split('-')[0].strip() if '-' in full else "")
            prefix = f"YLSHA{customer_code}" if customer_code else "YLSHA"
            cursor.execute("SELECT order_no FROM orders WHERE order_no LIKE ? ORDER BY order_no DESC LIMIT 1", (f"{prefix}%",))
            last = cursor.fetchone()
            seq = int(last['order_no'][len(prefix):]) + 1 if last and len(last['order_no']) > len(prefix) else 1
            order_no = f"{prefix}{seq:010d}"
        cursor.execute("""INSERT INTO orders (customer_name, order_no, channel, warehouse, boxes, total_weight, cbm, warehouse_code, receiver_name, address1, address2, city, state, zip_code, phone, phone2, is_customs, kg_price, business_no, vessel_voyage, volume_price, volume_ratio, product_name, fba_no, is_non_standard, expected_arrival, warehouse_note, order_note, delivery_requirement, generate_bill, status, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.get("customer_name"), order_no, data.get("channel"), data.get("warehouse", "铁士"), data.get("boxes", 0), data.get("total_weight", 0), data.get("cbm", 0), data.get("warehouse_code", ""), data.get("receiver_name", ""), data.get("address1", ""), data.get("address2", ""), data.get("city", ""), data.get("state", ""), data.get("zip_code", ""), data.get("phone", ""), data.get("phone2", ""), 1 if data.get("is_customs") else 0, data.get("kg_price"), data.get("business_no", ""), data.get("vessel_voyage", ""), data.get("volume_price"), data.get("volume_ratio"), data.get("product_name", ""), data.get("fba_no", ""), 1 if data.get("is_non_standard") else 0, data.get("expected_arrival", ""), data.get("warehouse_note", ""), data.get("order_note", ""), data.get("delivery_requirement", ""), 1 if data.get("generate_bill") else 0, "待入库", now, data.get("created_by", "system")))
        conn.commit()
        conn.close()
        return {"success": True, "message": "订单保存成功", "order_no": order_no}
    except Exception as e:
        print(f"❌ 创建订单错误：{e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}")
async def update_order(order_id: int, request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""UPDATE orders SET customer_name=?, order_no=?, channel=?, warehouse=?, boxes=?, total_weight=?, cbm=?, warehouse_code=?, receiver_name=?, address1=?, address2=?, city=?, state=?, zip_code=?, phone=?, phone2=?, is_customs=?, kg_price=?, business_no=?, vessel_voyage=?, volume_price=?, volume_ratio=?, product_name=?, fba_no=?, is_non_standard=?, delivery_requirement=?, expected_arrival=?, warehouse_note=?, order_note=?, generate_bill=?, status=?, updated_at=? WHERE id=?""",
            (data.get("customer_name"), data.get("order_no"), data.get("channel"), data.get("warehouse", "铁士"), data.get("boxes", 0), data.get("total_weight", 0), data.get("cbm", 0), data.get("warehouse_code", ""), data.get("receiver_name", ""), data.get("address1", ""), data.get("address2", ""), data.get("city", ""), data.get("state", ""), data.get("zip_code", ""), data.get("phone", ""), data.get("phone2", ""), 1 if data.get("is_customs") else 0, data.get("kg_price"), data.get("business_no", ""), data.get("vessel_voyage", ""), data.get("volume_price"), data.get("volume_ratio"), data.get("product_name", ""), data.get("fba_no", ""), 1 if data.get("is_non_standard") else 0, data.get("delivery_requirement", ""), data.get("expected_arrival", ""), data.get("warehouse_note", ""), data.get("order_note", ""), 1 if data.get("generate_bill") else 0, data.get("status", "待入库"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id))
        conn.commit()
        conn.close()
        return {"success": True, "message": "订单更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int, request: Request):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "订单已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 客户管理 =================
@app.get("/api/customers")
async def get_customers(search: str = Query(None)):
    conn = get_db()
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT * FROM customers WHERE customer_name LIKE ? OR company_name LIKE ?", (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM customers")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/customers")
async def create_customer(request: Request):
    try:
        data = await request.json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO customers (customer_name, tax_no, company_name, bank_account, finance_contact, finance_phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data.get("customer_name"), data.get("tax_no"), data.get("company_name"), data.get("bank_account"), data.get("finance_contact"), data.get("finance_phone"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return {"success": True, "message": "客户创建成功"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="客户名称已存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: int, request: Request):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "客户已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= 账单（占位） =================
@app.get("/api/bills")
async def get_bills():
    return []

@app.post("/api/bills")
async def create_bill(request: Request):
    return {"success": True, "message": "账单功能开发中"}

# ================= PDF生成 =================
def build_download_headers(filename: str):
    encoded_filename = quote(filename)
    return {
        "Content-Disposition": f"attachment; filename=download.pdf; filename*=UTF-8\'\'{encoded_filename}"
    }

@app.get("/api/orders/{order_id}/warehouse-pdf")
async def generate_warehouse_pdf(order_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order = dict(order)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(w/2, h - 1.5*cm, "上海洋山芦潮港仓库")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2, h - 2*cm, "进仓通知单")
    c.line(2*cm, h - 2.3*cm, w - 2*cm, h - 2.3*cm)
    
    y = h - 3.5*cm
    c.setFont("Helvetica", 11)
    items = [("进仓单号：", order['order_no']), ("产品渠道：", order['channel'] or '-'), ("备注：", order['order_note'] or '-'), ("件数：", f"{order['boxes']}件"), ("毛重：", f"{order['total_weight']} KG"), ("体积：", f"{order['cbm']} m³")]
    for label, value in items:
        c.drawString(2*cm, y, label)
        c.drawString(5*cm, y, value)
        y -= 0.7*cm
    y -= 0.5*cm
    c.line(2*cm, y, w - 2*cm, y)
    y -= 1*cm
    wh = [("仓库名称：", "悦路供应链管理（洋山芦潮港仓）"), ("仓库地址：", "上海浦东新区芦潮港洋浩路608号 B213、214、B115仓库"), ("联系电话：", "20936357-8030、8031（24小时）"), ("联系人：", "徐龙军"), ("联系方式：", "187-5547-9635")]
    for label, value in wh:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, label)
        c.setFont("Helvetica", 11)
        c.drawString(4.5*cm, y, value)
        y -= 0.7*cm
    y -= 0.5*cm
    c.drawString(2*cm, y, "如货物情况有变化，烦请及时通知我司操作。")
    y -= 1.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "路线描述：")
    y -= 0.5*cm
    route = "沿沪芦高速/S2经临港收费站，往东海大桥方向到两港大道出口下，往南芦公路方向靠右行驶过立交桥后往同顺大道方向，前面第一个红绿灯左转上同顺大道向东行驶至江山路右转，沿江山路行驶至洋浩路右转，沿洋浩路行驶100米靠右侧第一个园区大门进。"
    lines = simpleSplit(route, "Helvetica", 9, w - 4*cm)
    c.setFont("Helvetica", 9)
    for line in lines:
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
    y -= 0.8*cm
    c.line(2*cm, y, w - 2*cm, y)
    y -= 1*cm
    c.setFont("Helvetica", 9)
    c.drawCentredString(w/2, y, "地址：上海市杨浦区霍山路777号A栋515室")
    y -= 0.5*cm
    c.drawCentredString(w/2, y, "统一社会信用代码：91310000MA1H36FC05")
    y -= 0.5*cm
    c.drawCentredString(w/2, y, "电话：021-31827888    网址：www.quickway-sc.com")
    
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h - 1.5*cm, "图一：仓库位置图")
    map_path = os.path.join(os.path.dirname(__file__), "static", "map.png")
    if os.path.exists(map_path):
        c.drawImage(map_path, 1.5*cm, 2*cm, width=w - 3*cm, height=h - 5*cm, preserveAspectRatio=True, anchor='c')
    else:
        c.setFont("Helvetica", 12)
        c.drawCentredString(w/2, h/2, "（仓库位置图缺失：backend/static/map.png）")

    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, h - 1.5*cm, "图二：入园区示意图")
    layout_path = os.path.join(os.path.dirname(__file__), "static", "layout.png")
    if os.path.exists(layout_path):
        c.drawImage(layout_path, 1.5*cm, 2*cm, width=w - 3*cm, height=h - 5*cm, preserveAspectRatio=True, anchor='c')
    else:
        c.setFont("Helvetica", 12)
        c.drawCentredString(w/2, h/2, "（园区平面示意图缺失：backend/static/layout.png）")
    c.save()
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers=build_download_headers(f"入仓单_{order['order_no']}.pdf"))

@app.get("/api/orders/{order_id}/labels-pdf")
async def generate_labels_pdf(order_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order = dict(order)
    boxes = order['boxes'] or 1
    weight_per_box = (order['total_weight'] or 0) / boxes
    customer_code = ""
    if order['customer_name']:
        if ' - ' in order['customer_name']:
            customer_code = order['customer_name'].split(' - ')[0].strip()
        elif '-' in order['customer_name']:
            customer_code = order['customer_name'].split('-')[0].strip()
    label_w, label_h = 10*cm, 20*cm
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(label_w, label_h))
    for i in range(1, boxes + 1):
        if i > 1:
            c.showPage()
        y = label_h - 1*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(label_w/2, y, "YL_Supply Chain")
        y -= 1*cm
        c.setFont("Helvetica", 10)
        c.drawString(0.8*cm, y, f"产品名称：{order['channel'] or '美国海运-普船'}")
        y -= 0.8*cm
        c.drawString(0.8*cm, y, f"客户代码：{customer_code}")
        y -= 0.8*cm
        c.drawString(0.8*cm, y, f"重量：{weight_per_box:.1f}KG 邮编：{order['zip_code'] or '-'}")
        y -= 1.2*cm
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(label_w/2, y, "订单号")
        y -= 0.8*cm
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(label_w/2, y, order['order_no'])
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(label_w/2, y, f"{i}/{boxes} MADE IN CHINA")
        y -= 1.5*cm
        c.setFont("Helvetica", 10)
        c.drawCentredString(label_w/2, y, "子单号")
        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(label_w/2, y, f"{order['order_no']}_{i:03d}")
    c.save()
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers=build_download_headers(f"箱唛_{order['order_no']}.pdf"))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 物流管理系统启动成功！")
    print("📍 访问：http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)