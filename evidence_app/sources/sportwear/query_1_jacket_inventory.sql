WITH jackets AS (
    SELECT
        product_id,
        product_name,
        category_name,
        colour_name,
        size_name,
        gender_name
    FROM refined.products
    WHERE category_name ILIKE '%jacket%'
),
stock_by_variant AS (
    SELECT
        i.store_name,
        j.product_name,
        j.colour_name,
        COALESCE(SUM(i.amount), 0) AS total_stock,
        COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XS'), 0) AS xs,
        COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'S'), 0) AS s,
        COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'M'), 0) AS m,
        COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'L'), 0) AS l,
        COALESCE(SUM(i.amount) FILTER (WHERE j.size_name = 'XL'), 0) AS xl,
        COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Male'), 0) AS male,
        COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Female'), 0) AS female,
        COALESCE(SUM(i.amount) FILTER (WHERE j.gender_name = 'Unisex'), 0) AS unisex
    FROM jackets j
    JOIN refined.inventories i
        ON i.product_id = j.product_id
    GROUP BY
        i.store_name,
        j.product_name,
        j.colour_name
)
SELECT
    store_name,
    product_name,
    colour_name,
    total_stock,
    xs,
    s,
    m,
    l,
    xl,
    male,
    female,
    unisex,
    CASE
        WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
        WHEN total_stock < 10 THEN 'LOW_STOCK'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN xs > 0 AND s > 0 AND m > 0 AND l > 0 AND xl > 0 THEN 'FULL_SIZE_COVERAGE'
        WHEN xs > 0 OR s > 0 OR m > 0 OR l > 0 OR xl > 0 THEN 'PARTIAL_SIZE_COVERAGE'
        ELSE 'NO_SIZE_COVERAGE'
    END AS size_coverage_status
FROM stock_by_variant
ORDER BY store_name, product_name, colour_name;