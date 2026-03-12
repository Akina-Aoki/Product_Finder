-- Query 1: Current stock per product across all stores
SELECT
    p.product_id,
    p.product_name,
    SUM(i.amount) AS current_total_stock
FROM staging.products p
JOIN staging.inventories i
    ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name
ORDER BY current_total_stock DESC, p.product_name;


-- Query 2: Current stock by product and store
SELECT
    s.store_name,
    s.city,
    p.product_id,
    p.product_name,
    i.amount AS current_stock,
    i.update_date
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
ORDER BY s.store_name, p.product_name;

-- Query 3: Low-stock products (threshold can be adjusted)
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

-- Query 4: Total inventory volume by store
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

-- Query 5: Number of active products per category
SELECT
    c.category_name,
    COUNT(*) AS active_product_count
FROM staging.products p
JOIN staging.categories c
    ON p.category_id = c.category_id
WHERE p.active = true
GROUP BY c.category_name
ORDER BY active_product_count DESC, c.category_name;

-- Query 6: Estimated inventory value by product
SELECT
    p.product_id,
    p.product_name,
    SUM(i.amount) AS total_stock,
    p.price,
    SUM(i.amount * p.price) AS inventory_value
FROM staging.products p
JOIN staging.inventories i
    ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name, p.price
ORDER BY inventory_value DESC, p.product_name;

-- Query 7: Estimated inventory value by store
SELECT
    s.store_id,
    s.store_name,
    s.city,
    SUM(i.amount * p.price) AS store_inventory_value
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY s.store_id, s.store_name, s.city
ORDER BY store_inventory_value DESC, s.store_name;

-- Query 8: Top selling products by quantity sold
SELECT
    p.product_id,
    p.product_name,
    SUM(it.quantity) AS total_units_sold
FROM staging.items it
JOIN staging.products p
    ON it.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_units_sold DESC, p.product_name;


-- Query 9: Revenue per product
SELECT
    p.product_id,
    p.product_name,
    SUM(it.quantity * it.item_price) AS total_revenue
FROM staging.items it
JOIN staging.products p
    ON it.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC, p.product_name;



-- Query 10: Revenue by store
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

-- Query 11: Sales by day
SELECT
    DATE(o.order_date) AS sales_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_price) AS total_revenue
FROM staging.orders o
GROUP BY DATE(o.order_date)
ORDER BY sales_date;


-- Query 12: Lowest-performing products by quantity sold
SELECT
    p.product_id,
    p.product_name,
    COALESCE(SUM(it.quantity), 0) AS total_units_sold
FROM staging.products p
LEFT JOIN staging.items it
    ON p.product_id = it.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_units_sold ASC, p.product_name;