-------------------------------------------
-- Create 3 Store Records (UK Based)
INSERT INTO STORE (branch_number, address)
VALUES 
  ('BR001', 'Harrods, 87-135 Brompton Road, Knightsbridge, London, SW1X 7XL'),
  ('BR002', 'Selfridges, 400 Oxford Street, London, W1A 1AB'),
  ('BR003', 'Liberty, Regent Street, London, W1B 5AH');

-------------------------------------------
-- Insert Inventory for Each Store
-- Store 1:
-- Personal Inventory (e.g., product_id = 1)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (1, 1, 50, 10, '2025-03-01');

-- Home Inventory (e.g., product_id = 101)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (1, 101, 30, 5, '2025-03-02');

-- Store 2:
-- Personal Inventory (e.g., product_id = 2)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (2, 2, 60, 15, '2025-03-03');

-- Home Inventory (e.g., product_id = 102)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (2, 102, 25, 5, '2025-03-04');

-- Store 3:
-- Personal Inventory (e.g., product_id = 3)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (3, 3, 40, 8, '2025-03-05');

-- Home Inventory (e.g., product_id = 103)
INSERT INTO INVENTORY (store_id, product_id, quantity, restocking_threshold, last_restocking_date)
VALUES (3, 103, 35, 7, '2025-03-06');