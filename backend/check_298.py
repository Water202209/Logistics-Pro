import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 查询所有包含298的客户
cursor.execute("SELECT id, customer_name FROM customers WHERE customer_name LIKE '%298%'")
rows = cursor.fetchall()

print("📋 数据库中包含 '298' 的客户：")
for row in rows:
    print(f"  ID: {row[0]}, 名称: {row[1]}")

# 查询 SHYQH
cursor.execute("SELECT id, customer_name FROM customers WHERE customer_name LIKE '%SHYQH%'")
row = cursor.fetchone()
if row:
    print(f"\n✅ 找到 SHYQH: ID={row[0]}, 名称={row[1]}")
else:
    print(f"\n❌ 未找到 SHYQH")

# 查询 SHJH
cursor.execute("SELECT id, customer_name FROM customers WHERE customer_name LIKE '%SHJH%'")
row = cursor.fetchone()
if row:
    print(f"✅ 找到 SHJH: ID={row[0]}, 名称={row[1]}")
else:
    print(f"❌ 未找到 SHJH")

conn.close()