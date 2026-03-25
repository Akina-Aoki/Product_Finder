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
SELECT DISTINCT
    store_name AS store_value,
    store_name AS store_label 
FROM sportwear.meta_stores 
ORDER BY store_label
```

```sql filter_products
SELECT DISTINCT
    product_name AS product_value,
    product_name AS product_label
FROM sportwear.data_products
ORDER BY product_label
```

```sql filter_stock_status
SELECT 'OK' AS stock_status_value, 'OK' AS stock_status_label
UNION ALL SELECT 'LOW_STOCK', 'Low Stock'
UNION ALL SELECT 'OUT_OF_STOCK', 'Out of Stock'
```

```sql filter_colours
SELECT DISTINCT
    colour_name AS colour_value,
    colour_name AS colour_label 
FROM sportwear.meta_colours
ORDER BY colour_label
```

```sql filter_categories
SELECT DISTINCT
    category_name AS category_value,
    category_name AS category_label 
FROM sportwear.meta_categories
ORDER BY category_label
```

```sql filter_critical_stock
SELECT 'LOW_STOCK' AS status_value, 'Low Stock (1-9)' AS status_label
UNION ALL 
SELECT 'OUT_OF_STOCK', 'Out of Stock (0)'
```

<div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
  <Dropdown data={filter_stores} name="inventory_store" value=store_value label=store_label title="Store">
    <DropdownOption value="%" valueLabel="All Stores" />
  </Dropdown>
  
  <Dropdown data={filter_products} name="inventory_product" value=product_value label=product_label title="Product">
    <DropdownOption value="%" valueLabel="All Products" />
  </Dropdown>

  <Dropdown data={filter_stock_status} name="inventory_stock_status" value=stock_status_value label=stock_status_label title="Stock status">
    <DropdownOption value="%" valueLabel="All stock statuses" />
  </Dropdown>

  <Dropdown data={filter_colours} name="inventory_colour" value=colour_value label=colour_label title="Colour">
    <DropdownOption value="%" valueLabel="All colours" />
  </Dropdown>

  <Dropdown data={filter_categories} name="inventory_category" value=category_value label=category_label title="Category">
    <DropdownOption value="%" valueLabel="All categories" />
  </Dropdown>
</div>

```sql query_1_kpis
WITH normalized_inventory AS (
    SELECT
        inventory_id,
        store_name,
        category AS category_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
store_variant_stock AS (
    SELECT
        inventory_id,
        store_name,
        product_id,
        product_name,
        colour_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
    GROUP BY inventory_id, store_name, product_id, product_name, colour_name
),
classified_stock AS (
    SELECT
        *,
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
            ELSE 'OK'
        END AS stock_status_value
    FROM store_variant_stock
),
filtered_stock AS (
    SELECT *
    FROM classified_stock
    WHERE stock_status_value LIKE '${inputs.inventory_stock_status.value}'
)
SELECT
    COUNT(DISTINCT product_name) AS products,
    COUNT(DISTINCT store_name) AS stores_covered,
    COALESCE(SUM(total_stock), 0) AS total_units,
    COUNT(DISTINCT inventory_id) FILTER (WHERE stock_status_value = 'LOW_STOCK') AS low_stock_variants,
    COUNT(DISTINCT inventory_id) FILTER (WHERE stock_status_value = 'OUT_OF_STOCK') AS out_of_stock_variants,
    COUNT(DISTINCT inventory_id) FILTER (WHERE stock_status_value = 'OK') AS ok_stock_variants
FROM filtered_stock
``` 

<BigValue data={query_1_kpis} value=total_units title="Total stock units" />

<Grid cols=3>
  <BigValue data={query_1_kpis} value=products title="Products" />
  <BigValue data={query_1_kpis} value=stores_covered title="Stores covered" />
  <BigValue data={query_1_kpis} value=out_of_stock_variants title="Out of stock variants" />
</Grid>

<Grid cols=2>
  <BigValue data={query_1_kpis} value=low_stock_variants title="Low stock variants" />
  <BigValue data={query_1_kpis} value=ok_stock_variants title="OK stock variants" />
</Grid>

```sql query_1_status_summary
WITH normalized_inventory AS (
    SELECT
        inventory_id,
        store_name,
        category AS category_name,
        product AS product_name,
        colour AS colour_name,
        product_id,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
store_variant_stock AS (
    SELECT
        inventory_id,
        store_name,
        product_id,
        product_name,
        colour_name,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
    GROUP BY inventory_id, store_name, product_id, product_name, colour_name
),
classified_stock AS (
    SELECT
        *,
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
            ELSE 'OK'
        END AS stock_status_value,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM store_variant_stock
),
filtered_stock AS (
    SELECT *
    FROM classified_stock
    WHERE stock_status_value LIKE '${inputs.inventory_stock_status.value}'
)
SELECT
    stock_status,
    COUNT(DISTINCT inventory_id) AS store_variants_in_status,
    SUM(total_stock) AS units_in_status
FROM filtered_stock
GROUP BY stock_status
ORDER BY store_variants_in_status DESC, stock_status
```

## Stock status summary

<BarChart 
  data={query_1_status_summary} 
  x=stock_status 
  y=store_variants_in_status 
  title="Store placements by stock status" 
/>

<DataTable data={query_1_status_summary} />

```sql query_action_list
WITH normalized_inventory AS (
    SELECT
        inventory_id,
        store_name,
        category AS category_name,
        product_id,
        product AS product_name,
        brand,
        colour AS colour_name,
        size,
        gender,
        COALESCE(amount, 0) AS amount
    FROM sportwear.data_inventories
),
store_variant_stock AS (
    SELECT
        inventory_id,
        store_name,
        product_id,
        product_name,
        brand,
        colour_name,
        size,
        gender,
        SUM(amount) AS total_stock
    FROM normalized_inventory
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
    GROUP BY inventory_id, store_name, product_id, product_name, brand, colour_name, size, gender
),
classified_stock AS (
    SELECT
        store_name,
        product_name,
        product_id,
        brand,
        gender,
        size,
        colour_name,
        total_stock,
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
        END AS stock_status_value,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
        END AS status
    FROM store_variant_stock
    WHERE total_stock < 10
)
SELECT *
FROM classified_stock
WHERE (
    '${inputs.critical_stock_filter.value}' = '%'
    OR stock_status_value = '${inputs.critical_stock_filter.value}'
)
ORDER BY total_stock ASC, store_name, brand, product_name
```

<Dropdown 
    data={filter_critical_stock} 
    name="critical_stock_filter" 
    value=status_value 
    label=status_label 
    title="Filter list by urgency"
>
    <DropdownOption value="%" valueLabel="Show both (All under 10)" />
</Dropdown>

<DataTable data={query_action_list} search=true rows=15>
    <Column id=store_name title="Store" />
    <Column id=brand title="Brand" />
    <Column id=product_name title="Product" />
    <Column id=product_id title="Product ID" />
    <Column id=gender title="Gender" />
    <Column id=size title="Size" />
    <Column id=colour_name title="Colour" />
    <Column id=total_stock title="Stock Level" />
    <Column id=status title="Status" />
</DataTable>

```sql query_1_all_products
WITH normalized_inventory AS (
    SELECT
        store_name,
        category AS category_name,
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
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
    GROUP BY product_name, colour_name
),
final_stock AS (
    SELECT
        product_name,
        colour_name,
        total_stock,
        CASE
            WHEN total_stock = 0 THEN 'OUT_OF_STOCK'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'LOW_STOCK'
            ELSE 'OK'
        END AS stock_status_value,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM product_stock
)
SELECT 
    product_name,
    colour_name,
    total_stock,
    stock_status
FROM final_stock
WHERE stock_status_value LIKE '${inputs.inventory_stock_status.value}'
ORDER BY total_stock ASC, product_name, colour_name
```

## Product Stock

<DataTable data={query_1_all_products} search=true rows=10>
  <Column id=product_name title="Product" />
  <Column id=colour_name title="Colour" />
  <Column id=total_stock title="Total Stock Level" />
  <Column id=stock_status title="Status" />
</DataTable>

```sql query_1_per_store
WITH normalized_inventory AS (
    SELECT
        store_name,
        product AS product_name,
        category AS category_name,
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
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
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
        END AS stock_status_value,
        CASE
            WHEN total_stock = 0 THEN 'Out of Stock'
            WHEN total_stock BETWEEN 1 AND 9 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM store_product_stock
)
SELECT 
    store_name,
    product_name,
    colour_name,
    total_stock,
    stock_status
FROM final_stock
WHERE stock_status_value LIKE '${inputs.inventory_stock_status.value}'
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
    WHERE store_name LIKE '${inputs.inventory_store.value}'
      AND category_name LIKE '${inputs.inventory_category.value}'
      AND product_name LIKE '${inputs.inventory_product.value}'
      AND colour_name LIKE '${inputs.inventory_colour.value}'
    GROUP BY store_name, product_name, colour_name
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