SELECT
    s.store_name,
    s.city,
    c.category_name AS category,
    SUM(i.amount) AS total_stock,
    SUM(i.amount * p.price) AS estimated_inventory_value
FROM staging.inventories i
JOIN staging.products p
    ON i.product_id = p.product_id
JOIN staging.categories c
    ON p.category_id = c.category_id
JOIN staging.stores s
    ON i.store_id = s.store_id
GROUP BY
    s.store_name,
    s.city,
    c.category_name
ORDER BY
    s.store_name,
    estimated_inventory_value DESC,
    category;