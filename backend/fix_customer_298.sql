-- 修复298客户数据

-- 1. 如果存在错误的298 - SHJH，删除它
DELETE FROM customers WHERE customer_name = '298 - SHJH';

-- 2. 检查是否存在 SHYQH，如果不存在则插入
INSERT OR IGNORE INTO customers (customer_name, tax_no, company_name, created_at) 
VALUES ('298 - SHYQH', '', '', datetime('now'));

-- 3. 验证结果
SELECT '✅ 修复后的298客户：' || customer_name FROM customers WHERE customer_name LIKE '%298%';