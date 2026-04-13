-- 补充缺失的客户 298
INSERT OR IGNORE INTO customers (customer_name, tax_no, company_name, created_at) 
VALUES ('298 - SHJH', '', '', datetime('now'));

-- 显示最终客户数量
SELECT '✅ 客户总数：' || COUNT(*) FROM customers;