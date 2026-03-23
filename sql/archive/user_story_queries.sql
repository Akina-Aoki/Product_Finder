-- =====================================================
-- Product_Finder
-- SAFEST WORKING VERSION BASED ON CONFIRMED SCHEMA
-- =====================================================

-- NOTE:
-- refined.inventories confirmed columns:
-- inventory_id, product_id, product_name, amount, store_name, city, update_date
--
-- refined.categories does not exist.
-- Therefore:
-- - inventory-only queries use refined.inventories
-- - category / pricing / revenue / sales queries use staging tables


-- =====================================================
-- A. TRACK PRODUCT MOVEMENT ACROSS INVENTORY
-- =====================================================

-- Query 1:
-- FINAL --- DO WE HAVE FULL SIZE COVERAGE?
WITH jackets AS (
    SELECT *
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'
)

SELECT
    i.store_name,
    j.product_name,

    COALESCE(SUM(i.amount), 0) AS total_stock,

    -- Sizes (NULL → 0)
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XS'), 0) AS xs,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'S'), 0)  AS s,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'M'), 0)  AS m,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'L'), 0)  AS l,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XL'), 0) AS xl,

    -- Gender
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Male'), 0)   AS male,
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Female'), 0) AS female,
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Unisex'), 0) AS unisex,

    -- Business classification (safe)
    CASE
        WHEN COALESCE(SUM(i.amount), 0) = 0 THEN 'OUT OF STOCK'
        WHEN COALESCE(SUM(i.amount), 0) < 10 THEN 'LOW STOCK'
        ELSE 'OK'
    END AS stock_status

FROM jackets j
JOIN refined.inventories i
    ON i.product_id = j.product_id

GROUP BY i.store_name, j.product_name
ORDER BY total_stock DESC;



-- Current stock per product across all stores
WITH jackets AS (
    SELECT *
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'
)

SELECT
    j.product_name,

    SUM(i.amount) AS total_stock,

    
    COALESCE(SUM(i.amount), 0) AS total_stock,

    -- Size distribution
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XS'), 0) AS stock_xs,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'S'), 0)  AS stock_s,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'M'), 0)  AS stock_m,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'L'), 0)  AS stock_l,
    COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XL'), 0) AS stock_xl,

    -- Gender distribution
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Male'), 0)   AS stock_male,
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Female'), 0) AS stock_female,
    COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Unisex'), 0) AS stock_unisex

FROM jackets j
JOIN refined.inventories i
    ON i.product_id = j.product_id

GROUP BY j.product_name
ORDER BY total_stock DESC;





-- Now divide it into smaller views per store
WITH  AS (                      ----- adjust category name here
    SELECT *
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'   ----- adjust category name here
)

SELECT
    i.store_name,
    j.product_name,

    SUM(i.amount) AS total_stock,

    -- Size distribution
    SUM(i.amount) FILTER (WHERE j.size_name = 'XS') AS stock_xs,
    SUM(i.amount) FILTER (WHERE j.size_name = 'S')  AS stock_s,
    SUM(i.amount) FILTER (WHERE j.size_name = 'M')  AS stock_m,
    SUM(i.amount) FILTER (WHERE j.size_name = 'L')  AS stock_l,
    SUM(i.amount) FILTER (WHERE j.size_name = 'XL') AS stock_xl,

    -- Gender distribution
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Male')   AS stock_male,
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Female') AS stock_female,
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Unisex') AS stock_unisex

FROM jackets j                           ----- adjust category name here
JOIN refined.inventories i
    ON i.product_id = j.product_id

WHERE i.store_name = 'Gallerian_Centrum'   -- adjust to actual name

GROUP BY i.store_name, j.product_name
ORDER BY total_stock DESC;



-- Or BY COLOR
WITH jackets AS (                       ----- adjust category name here
    SELECT *
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'       -- adjust to actual name
)

SELECT
    i.store_name,
    j.product_name,
    j.colour_name,

    SUM(i.amount) AS total_stock,

    -- Sizes
    SUM(i.amount) FILTER (WHERE j.size_name = 'XS') AS xs,
    SUM(i.amount) FILTER (WHERE j.size_name = 'S')  AS s,
    SUM(i.amount) FILTER (WHERE j.size_name = 'M')  AS m,
    SUM(i.amount) FILTER (WHERE j.size_name = 'L')  AS l,
    SUM(i.amount) FILTER (WHERE j.size_name = 'XL') AS xl,

    -- Gender
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Male')   AS male,
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Female') AS female,
    SUM(i.amount) FILTER (WHERE j.gender_name = 'Unisex') AS unisex

FROM jackets j                              -- adjust to actual name
JOIN refined.inventories i
    ON i.product_id = j.product_id

GROUP BY
    i.store_name,
    j.product_name,
    j.colour_name

ORDER BY
    i.store_name,
    total_stock DESC;


--- WITH STOCK STATUS
WITH jackets AS (               -- adjust to actual name
    SELECT *
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'        -- adjust to actual name
)

SELECT
    i.store_name,
    j.product_name,

    SUM(i.amount) AS total_stock,

    -- Sizes
    SUM(i.amount) FILTER (WHERE j.size_name = 'XS') AS xs,
    SUM(i.amount) FILTER (WHERE j.size_name = 'S')  AS s,
    SUM(i.amount) FILTER (WHERE j.size_name = 'M')  AS m,
    SUM(i.amount) FILTER (WHERE j.size_name = 'L')  AS l,
    SUM(i.amount) FILTER (WHERE j.size_name = 'XL') AS xl,

    -- Colors (Top-level visibility)
    COUNT(DISTINCT j.colour_name) AS color_variants,

    -- Gender coverage
    COUNT(DISTINCT j.gender_name) AS gender_variants,

    CASE
        WHEN SUM(i.amount) = 0 THEN 'OUT OF STOCK'
        WHEN SUM(i.amount) < 10 THEN 'LOW STOCK'
        ELSE 'OK'
    END AS stock_health

FROM jackets j              -- adjust to actual name
JOIN refined.inventories i
    ON i.product_id = j.product_id

GROUP BY i.store_name, j.product_name
ORDER BY total_stock DESC;


























-- Query 2: OK
-- Current stock by product and store
SELECT
    i.inventory_id,
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    i.amount AS current_stock,
    i.update_date
FROM refined.inventories i
ORDER BY i.store_name, i.product_name;


-- Query 3: OK
-- Low-stock products across all stores
-- Adjust threshold as needed
SELECT
    i.product_id,
    i.product_name,
    SUM(i.amount) AS current_total_stock
FROM refined.inventories i
GROUP BY i.product_id, i.product_name
HAVING SUM(i.amount) < 10
ORDER BY current_total_stock ASC, i.product_name;


-- Query 4: 
-- Out-of-stock products across all stores
SELECT
    i.product_id,
    i.product_name,
    SUM(i.amount) AS total_stock
FROM refined.inventories i
GROUP BY i.product_id, i.product_name
HAVING SUM(i.amount) = 0
ORDER BY i.product_name;


-- Query 5: OK
-- Total inventory quantity by store
SELECT
    i.store_name,
    i.city,
    SUM(i.amount) AS total_items_in_stock
FROM refined.inventories i
GROUP BY i.store_name, i.city
ORDER BY total_items_in_stock DESC, i.store_name;


-- Query 6:
-- Number of active products per category
SELECT
    c.category_name,
    COUNT(*) AS active_product_count
FROM staging.products p
JOIN staging.categories c
    ON p.category_id = c.category_id
WHERE p.active = TRUE
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
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    i.amount,
    i.update_date
FROM refined.inventories i
ORDER BY i.update_date DESC;


-- Query 24:
-- Most recently updated products across all stores
SELECT
    i.product_id,
    i.product_name,
    MAX(i.update_date) AS latest_inventory_update
FROM refined.inventories i
GROUP BY i.product_id, i.product_name
ORDER BY latest_inventory_update DESC, i.product_name;


-- Query 25:
-- Most recently updated products by store
SELECT
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    MAX(i.update_date) AS latest_inventory_update
FROM refined.inventories i
GROUP BY i.store_name, i.city, i.product_id, i.product_name
ORDER BY latest_inventory_update DESC, i.store_name, i.product_name;


-- Query 26:
-- Inventory updates by week
SELECT
    DATE_TRUNC('week', i.update_date) AS update_week,
    COUNT(*) AS inventory_updates
FROM refined.inventories i
GROUP BY DATE_TRUNC('week', i.update_date)
ORDER BY update_week;


-- Query 27:
-- Inventory updates by month
SELECT
    DATE_TRUNC('month', i.update_date) AS update_month,
    COUNT(*) AS inventory_updates
FROM refined.inventories i
GROUP BY DATE_TRUNC('month', i.update_date)
ORDER BY update_month;


-- Query 28:
-- Inventory updates by store and week
SELECT
    i.store_name,
    i.city,
    DATE_TRUNC('week', i.update_date) AS update_week,
    COUNT(*) AS inventory_updates
FROM refined.inventories i
GROUP BY i.store_name, i.city, DATE_TRUNC('week', i.update_date)
ORDER BY update_week, i.store_name;


-- Query 29:
-- Inventory updates by store and month
SELECT
    i.store_name,
    i.city,
    DATE_TRUNC('month', i.update_date) AS update_month,
    COUNT(*) AS inventory_updates
FROM refined.inventories i
GROUP BY i.store_name, i.city, DATE_TRUNC('month', i.update_date)
ORDER BY update_month, i.store_name;


-- Query 30:
-- Products most frequently updated in inventory
-- Proxy for products that may be constantly restocked
SELECT
    i.product_id,
    i.product_name,
    COUNT(*) AS inventory_record_count,
    MAX(i.update_date) AS latest_update
FROM refined.inventories i
GROUP BY i.product_id, i.product_name
ORDER BY inventory_record_count DESC, latest_update DESC;


-- Query 31:
-- Products most frequently updated in inventory by store
-- Proxy for products that may be constantly restocked in a specific store
SELECT
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    COUNT(*) AS inventory_record_count,
    MAX(i.update_date) AS latest_update
FROM refined.inventories i
GROUP BY i.store_name, i.city, i.product_id, i.product_name
ORDER BY inventory_record_count DESC, latest_update DESC, i.store_name;


-- Query 32:
-- Recently updated low-stock products
-- Useful for spotting products that may need frequent restocking attention
SELECT
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    i.amount,
    i.update_date
FROM refined.inventories i
WHERE i.amount < 10
ORDER BY i.update_date DESC, i.amount ASC;