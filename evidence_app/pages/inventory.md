---
title: Inventory
---

User Story & Minimum Viable Product:
- Track Product Movement
- Detect Restocking Events
- Inventory Updates

Use the filters below to answer the main KPI question:  
**Spot Stock Status** across stores, product groups, colours, and stock health.**

```sql filter_stores
SELECT '' AS store_value, 'All stores' AS store_label
UNION ALL
SELECT DISTINCT
    store_name AS store_value,
    store_name AS store_label
FROM sportwear.data_inventories
ORDER BY store_label
```

```sql filter_products
SELECT '' AS product_value, 'All products' AS product_label
UNION ALL
SELECT DISTINCT
    product AS product_value,
    product AS product_label
FROM sportwear.data_inventories
WHERE product IS NOT NULL
ORDER BY product_label
```

```sql filter_stock_status
SELECT '' AS stock_status_value, 'All stock statuses' AS stock_status_label
UNION ALL SELECT 'OK', 'OK'
UNION ALL SELECT 'LOW_STOCK', 'Low Stock'
UNION ALL SELECT 'OUT_OF_STOCK', 'Out of Stock'
```

```sql filter_colours
SELECT '' AS colour_value, 'All colours' AS colour_label
UNION ALL
SELECT DISTINCT
    colour AS colour_value,
    colour AS colour_label
FROM sportwear.data_inventories
WHERE colour IS NOT NULL
ORDER BY colour_label
```

<div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
  <Dropdown
    data={filter_stores}
    name="inventory_store"
    value=store_value
    label=store_label
    title="Store"
  />
  <Dropdown
    data={filter_products}
    name="inventory_product"
    value=product_value
    label=product_label
    title="Product"
  />
  <Dropdown
    data={filter_stock_status}
    name="inventory_stock_status"
    value=stock_status_value
    label=stock_status_label
    title="Stock status"
  />
  <Dropdown
    data={filter_colours}
    name="inventory_colour"
    value=colour_value
    label=colour_label
    title="Colour"
  />
</div>

```sql query_1_kpis
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
product_stock AS (
    SELECT
        store_name,
        product_name,
        colour_name,
        product_id,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE ('${inputs.inventory_store.value}' = '' OR store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR product_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR colour_name = '${inputs.inventory_colour.value}')
    GROUP BY store_name, product_name, colour_name, product_id
),
classified_stock AS (
    SELECT
        *,
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
            ELSE 'OK'
        END AS stock_status
    FROM product_stock
),
filtered_stock AS (
    SELECT *
    FROM classified_stock
    WHERE ('${inputs.inventory_stock_status.value}' = '' OR stock_status = '${inputs.inventory_stock_status.value}')
),
product_scope AS (
    SELECT
        product_name,
        SUM(total_stock) AS total_stock
    FROM filtered_stock
    GROUP BY product_name
),
status_scope AS (
    SELECT
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
            ELSE 'OK'
        END AS stock_status
    FROM product_scope
)
SELECT
    COUNT(DISTINCT product_name) AS products,
    COUNT(DISTINCT store_name) AS stores_covered,
    COALESCE(SUM(total_stock), 0) AS total_units,
    COUNT(*) FILTER (WHERE stock_status = 'LOW_STOCK') AS low_stock_products,
    COUNT(*) FILTER (WHERE stock_status = 'OUT_OF_STOCK') AS out_of_stock_products,
    COUNT(*) FILTER (WHERE stock_status = 'OK') AS ok_stock_products
FROM filtered_stock
```

<BigValue data={query_1_kpis} value=total_units title="Total stock units" />

<Grid cols=3>
  <BigValue data={query_1_kpis} value=products title="Products" />
  <BigValue data={query_1_kpis} value=stores_covered title="Stores covered" />
  <BigValue data={query_1_kpis} value=out_of_stock_products title="Out of stock products" />
</Grid>

<Grid cols=2>
  <BigValue data={query_1_kpis} value=low_stock_products title="Low stock products" />
  <BigValue data={query_1_kpis} value=ok_stock_products title="OK stock products" />
</Grid>

```sql query_1_status_summary
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
product_stock AS (
    SELECT
        product_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE ('${inputs.inventory_store.value}' = '' OR store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR product_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR colour_name = '${inputs.inventory_colour.value}')
    GROUP BY product_name
),
classified_stock AS (
    SELECT
        product_name,
        total_stock,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM product_stock
),
filtered_stock AS (
    SELECT *
    FROM classified_stock
    WHERE (
        '${inputs.inventory_stock_status.value}' = ''
        OR ('${inputs.inventory_stock_status.value}' = 'OUT_OF_STOCK' AND stock_status = 'Out of Stock')
        OR ('${inputs.inventory_stock_status.value}' = 'LOW_STOCK' AND stock_status = 'Low Stock')
        OR ('${inputs.inventory_stock_status.value}' = 'OK' AND stock_status = 'OK')
    )
)
SELECT
    stock_status,
    COUNT(*) AS products_in_status,
    SUM(total_stock) AS units_in_status
FROM filtered_stock
GROUP BY stock_status
ORDER BY products_in_status DESC, stock_status
```

## Stock status summary

<BarChart data={query_1_status_summary} x=stock_status y=products_in_status title="Products by stock status" />

<DataTable data={query_1_status_summary} />

```sql query_1_all_products
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
product_stock AS (
    SELECT
        product_name,
        colour_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE ('${inputs.inventory_store.value}' = '' OR store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR product_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR colour_name = '${inputs.inventory_colour.value}')
    GROUP BY product_name, colour_name
),
final_stock AS (
    SELECT
        product_name,
        colour_name,
        total_stock,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM product_stock
)
SELECT *
FROM final_stock
WHERE (
    '${inputs.inventory_stock_status.value}' = ''
    OR ('${inputs.inventory_stock_status.value}' = 'OUT_OF_STOCK' AND stock_status = 'Out of Stock')
    OR ('${inputs.inventory_stock_status.value}' = 'LOW_STOCK' AND stock_status = 'Low Stock')
    OR ('${inputs.inventory_stock_status.value}' = 'OK' AND stock_status = 'OK')
)
ORDER BY total_stock ASC, product_name, colour_name
```

## Current stock per product

<DataTable data={query_1_all_products} />

```sql query_1_per_store
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
store_product_stock AS (
    SELECT
        store_name,
        product_name,
        colour_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE ('${inputs.inventory_store.value}' = '' OR store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR product_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR colour_name = '${inputs.inventory_colour.value}')
    GROUP BY store_name, product_name, colour_name
),
final_stock AS (
    SELECT
        store_name,
        product_name,
        colour_name,
        total_stock,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM store_product_stock
)
SELECT *
FROM final_stock
WHERE (
    '${inputs.inventory_stock_status.value}' = ''
    OR ('${inputs.inventory_stock_status.value}' = 'OUT_OF_STOCK' AND stock_status = 'Out of Stock')
    OR ('${inputs.inventory_stock_status.value}' = 'LOW_STOCK' AND stock_status = 'Low Stock')
    OR ('${inputs.inventory_stock_status.value}' = 'OK' AND stock_status = 'OK')
)
ORDER BY store_name, total_stock ASC, product_name
```

## Store view

<DataTable data={query_1_per_store} />

<BarChart
  data={query_1_per_store}
  x=product_name
  y=total_stock
  series=store_name
  title="Stock by product and store"
/>

```sql query_1_stock_outliers
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
store_product_stock AS (
    SELECT
        store_name,
        product_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE ('${inputs.inventory_store.value}' = '' OR store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR product_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR colour_name = '${inputs.inventory_colour.value}')
    GROUP BY store_name, product_name
),
filtered_stock AS (
    SELECT *
    FROM store_product_stock
    WHERE (
        '${inputs.inventory_stock_status.value}' = ''
        OR ('${inputs.inventory_stock_status.value}' = 'OUT_OF_STOCK' AND total_stock = 0)
        OR ('${inputs.inventory_stock_status.value}' = 'LOW_STOCK' AND total_stock BETWEEN 1 AND 9)
        OR ('${inputs.inventory_stock_status.value}' = 'OK' AND total_stock >= 10)
    )
),
stock_stats AS (
    SELECT AVG(total_stock) AS avg_stock
    FROM filtered_stock
)
SELECT
    b.store_name,
    b.product_name,
    b.total_stock,
    ROUND(s.avg_stock, 2) AS average_stock,
    ROUND(b.total_stock - s.avg_stock, 2) AS stock_change_from_average,
    ROUND(ABS(b.total_stock - s.avg_stock), 2) AS absolute_change
FROM filtered_stock b
CROSS JOIN stock_stats s
ORDER BY absolute_change DESC, b.total_stock ASC, b.product_name
LIMIT 5
```

## Biggest outliers in stock level

<DataTable data={query_1_stock_outliers} />

<BarChart
  data={query_1_stock_outliers}
  x=product_name
  y=stock_change_from_average
  series=store_name
  title="Biggest stock outliers vs average"
/>