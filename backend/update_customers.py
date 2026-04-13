import sqlite3

def update_customers():
    """更新客户数据，只保留指定的12个客户"""
    
    # 需要保留的客户列表
    customers_to_keep = [
        ('262 - SHYQ', '', ''),
        ('268 - SHSC', '', ''),
        ('278 - SHJM', '', ''),
        ('298 - SHYQH', '', ''),
        ('309 - TC', '', ''),
        ('321 - MRMX', '', ''),
        ('378 - 天荣株式会社', '', ''),
        ('380 - 德立迅', '', ''),
        ('387 - INFINITY', '', ''),
        ('389 - 巴士悦信', '', ''),
        ('419 - 荣马', '', ''),
        ('431 - 威适攀', '', '')
    ]
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("🗑️  清空现有客户数据...")
    cursor.execute("DELETE FROM customers")
    
    print("📝 插入新客户数据...")
    now = '2026-04-11 00:00:00'
    for customer in customers_to_keep:
        try:
            cursor.execute("""
                INSERT INTO customers (customer_name, tax_no, company_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (customer[0], customer[1], customer[2], now))
            print(f"  ✅ {customer[0]}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  {customer[0]} (已存在)")
    
    conn.commit()
    
    # 统计数量
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ 客户数据更新完成！")
    print(f"📊 客户总数：{count}")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 开始更新客户数据...")
    print("=" * 60)
    update_customers()
    print("=" * 60)