-- =====================================================
-- Product_Finder

-- =====================================================
-- A. TRACK PRODUCT MOVEMENT ACROSS INVENTORY
-- =====================================================

-- Query 1:
-- Current stock per product across all stores
SELECT
    product_id,
    product_name,
    SUM(i.amount) AS current_total_stock
FROM refined.products p
JOIN staging.inventories i
GROUP BY product_id, product_name
ORDER BY current_total_stock DESC, p.product_name;


-- Query 2:
-- Current stock by product and store
SELECT
    inventory_id,
    store_name,
    city,
    product_id,
    product_name,
    amount AS current_stock,
    update_date
FROM refined.inventories 
ORDER BY store_name, product_name;


-- Extra for refined schema
-- Revenue per product
SELECT
  product_id,
  product_name,
  SUM(quantity * item_price) AS total_revenue
FROM refined.items
GROUP BY product_id, product_name
ORDER BY total_revenue DESC, product_name;

-- Revenue by store
SELECT
  store_name,
  city,
  SUM(quantity * item_price) AS total_store_revenue
FROM refined.items
GROUP BY store_name, city
ORDER BY total_store_revenue DESC, store_name;

-- Sales by day
SELECT
  DATE(order_date) AS sales_day,
  COUNT(DISTINCT order_id) AS total_orders,
  SUM(quantity * item_price) AS total_revenue
FROM refined.items
GROUP BY DATE(order_date)
ORDER BY sales_day;

-- Query 3:
-- Low-stock products across all stores
-- Adjust threshold as needed
SELECT
    p.product_id,
    p.product_name,
    SUM(i.amount) AS current_total_stock
FROM staging.products p
JOIN staging.inventories i
    ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(i.amount) < 10
ORDER BY current_total_stock ASC, p.product_name;


-- Query 4:
-- Out-of-stock products across all stores
SELECT
    p.product_id,
    p.product_name,
    SUM(i.amount) AS total_stock
FROM staging.products p
JOIN staging.inventories i
    ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(i.amount) = 0
ORDER BY p.product_name;


-- Query 5:
-- Total inventory quantity by store
SELECT
    s.store_id,
    s.store_name,
    s.city,
    SUM(i.amount) AS total_items_in_stock
FROM staging.stores s
JOIN staging.inventories i
    ON s.store_id = i.store_id
GROUP BY s.store_id, s.store_name, s.city
ORDER BY total_items_in_stock DESC, s.store_name;


-- Query 6:
-- Number of active products per category
SELECT
    c.category_name,
    COUNT(*) AS active_product_count
FROM staging.products p
JOIN staging.categories c
    ON p.category_id = c.category_id
WHERE p.active = true
GROUP BY c.category_name
ORDER BY active_product_count DESC, c.category_name;


-- Query 7:
-- Estimated inventory value remaining by product
SELECT
    p.product_id,
    p.product_name,
    SUM(i.amount) AS total_stock,
    p.price,
    SUM(i.amount * p.price) AS inventory_value_remaining
FROM staging.products p
JOIN staging.inventories i
    ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name, p.price
ORDER BY inventory_value_remaining DESC, p.product_name;


-- Query 8:
-- Estimated inventory value remaining by store
SELECT
    s.store_id,
    s.store_name,
    s.city,
    SUM(i.amount * p.price) AS store_inventory_value_remaining
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, s.city
ORDER BY store_inventory_value_remaining DESC, s.store_name;


-- Query 9:
-- Estimated inventory value remaining for the whole company
SELECT
    SUM(i.amount * p.price) AS total_company_inventory_value_remaining
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id;


-- =====================================================
-- B. ANALYZE REVENUE PERFORMANCE OF PRODUCTS
-- =====================================================

-- Query 10:
-- Revenue per product
SELECT
    p.product_id,
    p.product_name,
    SUM(it.quantity * it.item_price) AS total_revenue
FROM staging.items it
JOIN staging.products p
    ON it.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC, p.product_name;


-- Query 11:
-- Revenue by store
SELECT
    s.store_id,
    s.store_name,
    s.city,
    SUM(o.order_price) AS total_store_revenue
FROM staging.orders o
JOIN staging.stores s
    ON o.store_id = s.store_id
GROUP BY s.store_id, s.store_name, s.city
ORDER BY total_store_revenue DESC, s.store_name;


-- Query 12:
-- Total company revenue
SELECT
    SUM(o.order_price) AS total_company_revenue
FROM staging.orders o;


-- Query 13:
-- Sales by day
SELECT
    DATE(o.order_date) AS sales_day,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
GROUP BY DATE(o.order_date)
ORDER BY sales_day;


-- Query 14:
-- Sales by week
SELECT
    DATE_TRUNC('week', o.order_date) AS sales_week,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
GROUP BY DATE_TRUNC('week', o.order_date)
ORDER BY sales_week;


-- Query 15:
-- Sales by month
SELECT
    DATE_TRUNC('month', o.order_date) AS sales_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY sales_month;


-- Query 16:
-- Sales by day and store
SELECT
    s.store_id,
    s.store_name,
    DATE(o.order_date) AS sales_day,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
JOIN staging.stores s
    ON o.store_id = s.store_id
GROUP BY s.store_id, s.store_name, DATE(o.order_date)
ORDER BY sales_day, s.store_name;


-- Query 17:
-- Sales by week and store
SELECT
    s.store_id,
    s.store_name,
    DATE_TRUNC('week', o.order_date) AS sales_week,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
JOIN staging.stores s
    ON o.store_id = s.store_id
GROUP BY s.store_id, s.store_name, DATE_TRUNC('week', o.order_date)
ORDER BY sales_week, s.store_name;


-- Query 18:
-- Sales by month and store
SELECT
    s.store_id,
    s.store_name,
    DATE_TRUNC('month', o.order_date) AS sales_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
JOIN staging.stores s
    ON o.store_id = s.store_id
GROUP BY s.store_id, s.store_name, DATE_TRUNC('month', o.order_date)
ORDER BY sales_month, s.store_name;


-- =====================================================
-- C. IDENTIFY TOP AND LOW PERFORMING PRODUCTS
-- =====================================================

-- Query 19:
-- Highest-selling products by quantity sold
SELECT
    p.product_id,
    p.product_name,
    SUM(it.quantity) AS total_units_sold
FROM staging.items it
JOIN staging.products p
    ON it.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_units_sold DESC, p.product_name;


-- Query 20:
-- Lowest-performing products by quantity sold
SELECT
    p.product_id,
    p.product_name,
    COALESCE(SUM(it.quantity), 0) AS total_units_sold
FROM staging.products p
LEFT JOIN staging.items it
    ON p.product_id = it.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_units_sold ASC, p.product_name;


-- Query 21:
-- Top-performing products by revenue
SELECT
    p.product_id,
    p.product_name,
    SUM(it.quantity * it.item_price) AS total_revenue
FROM staging.items it
JOIN staging.products p
    ON it.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC, p.product_name;


-- Query 22:
-- Lowest-performing products by revenue
SELECT
    p.product_id,
    p.product_name,
    COALESCE(SUM(it.quantity * it.item_price), 0) AS total_revenue
FROM staging.products p
LEFT JOIN staging.items it
    ON p.product_id = it.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue ASC, p.product_name;


-- =====================================================
-- D. DETECT RESTOCKING EVENTS / REAL-TIME INVENTORY UPDATES
-- NOTE: These use inventory updates as a proxy for restocking
-- until a dedicated inventory events table is available.
-- =====================================================

-- Query 23:
-- Recently updated inventory records by product and store
SELECT
    s.store_id,
    s.store_name,
    p.product_id,
    p.product_name,
    i.amount,
    i.update_date
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
ORDER BY i.update_date DESC;


-- Query 24:
-- Most recently updated products across all stores
SELECT
    p.product_id,
    p.product_name,
    MAX(i.update_date) AS latest_inventory_update
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY latest_inventory_update DESC, p.product_name;


-- Query 25:
-- Most recently updated products by store
SELECT
    s.store_id,
    s.store_name,
    p.product_id,
    p.product_name,
    MAX(i.update_date) AS latest_inventory_update
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, p.product_id, p.product_name
ORDER BY latest_inventory_update DESC, s.store_name, p.product_name;


-- Query 26:
-- Inventory updates by week
SELECT
    DATE_TRUNC('week', i.update_date) AS update_week,
    COUNT(*) AS inventory_updates
FROM staging.inventories i
GROUP BY DATE_TRUNC('week', i.update_date)
ORDER BY update_week;


-- Query 27:
-- Inventory updates by month
SELECT
    DATE_TRUNC('month', i.update_date) AS update_month,
    COUNT(*) AS inventory_updates
FROM staging.inventories i
GROUP BY DATE_TRUNC('month', i.update_date)
ORDER BY update_month;


-- Query 28:
-- Inventory updates by store and week
SELECT
    s.store_id,
    s.store_name,
    DATE_TRUNC('week', i.update_date) AS update_week,
    COUNT(*) AS inventory_updates
FROM staging.inventories i
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, DATE_TRUNC('week', i.update_date)
ORDER BY update_week, s.store_name;


-- Query 29:
-- Inventory updates by store and month
SELECT
    s.store_id,
    s.store_name,
    DATE_TRUNC('month', i.update_date) AS update_month,
    COUNT(*) AS inventory_updates
FROM staging.inventories i
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, DATE_TRUNC('month', i.update_date)
ORDER BY update_month, s.store_name;


-- Query 30:
-- Products most frequently updated in inventory
-- Proxy for products that may be constantly restocked
SELECT
    p.product_id,
    p.product_name,
    COUNT(*) AS inventory_record_count,
    MAX(i.update_date) AS latest_update
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY inventory_record_count DESC, latest_update DESC;


-- Query 31:
-- Products most frequently updated in inventory by store
-- Proxy for products that may be constantly restocked in a specific store
SELECT
    s.store_id,
    s.store_name,
    p.product_id,
    p.product_name,
    COUNT(*) AS inventory_record_count,
    MAX(i.update_date) AS latest_update
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, p.product_id, p.product_name
ORDER BY inventory_record_count DESC, latest_update DESC, s.store_name;


-- Query 32:
-- Recently updated low-stock products
-- Useful for spotting products that may need frequent restocking attention
SELECT
    s.store_name,
    p.product_id,
    p.product_name,
    i.amount,
    i.update_date
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
WHERE i.amount < 10
ORDER BY i.update_date DESC, i.amount ASC