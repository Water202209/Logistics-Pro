#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
客户数据导入脚本
使用方法：python import_customers.py
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    """备份数据库"""
    if os.path.exists('data.db'):
        backup_file = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.system(f"copy data.db {backup_file}")
        print(f"✅ 数据库已备份为：{backup_file}")
    else:
        print("⚠️  未找到数据库文件，将创建新数据库")

def import_customers():
    """导入客户数据"""
    print("=" * 60)
    print("🚀 开始导入客户数据...")
    print("=" * 60)
    
    # 备份数据库
    backup_database()
    
    try:
        # 连接数据库
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open('import_customers.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL脚本
        cursor.executescript(sql_content)
        conn.commit()
        
        # 统计结果
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_count = cursor.fetchone()[0]
        
        print(f"✅ 导入完成！")
        print(f"📊 客户总数：{total_count}")
        print("=" * 60)
        
        # 显示前10个客户
        cursor.execute("SELECT customer_name FROM customers LIMIT 10")
        print("\n📋 前10个客户示例：")
        for row in cursor.fetchall():
            print(f"   - {row[0]}")
        
        conn.close()
        
    except FileNotFoundError:
        print("❌ 错误：未找到 import_customers.sql 文件")
        print("   请确保该文件与脚本在同一目录")
    except sqlite3.Error as e:
        print(f"❌ 数据库错误：{e}")
    except Exception as e:
        print(f"❌ 未知错误：{e}")

if __name__ == "__main__":
    import_customers()
    print("\n💡 提示：请重启后端服务以查看新客户")