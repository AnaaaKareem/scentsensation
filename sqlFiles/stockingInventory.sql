INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
SELECT s.store_id, p.product_id, 
       CASE WHEN p.product_id <= 12 THEN 50 ELSE 75 END AS quantity,
       CASE WHEN p.product_id <= 12 THEN 10 ELSE 15 END AS restocking_threshold,
       CURDATE() AS last_restocking_date
FROM STORE s
JOIN (
    SELECT product_id FROM PRODUCTS
    UNION ALL
    SELECT product_id + 12 FROM PRODUCTS
) p
ON 1=1;