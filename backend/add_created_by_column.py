import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

try:
    # 添加 created_by 字段
    cursor.execute("ALTER TABLE orders ADD COLUMN created_by TEXT")
    conn.commit()
    print("✅ 成功添加 created_by 字段到 orders 表")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️  字段已存在，无需添加")
    else:
        print(f"❌ 错误：{e}")

conn.close()