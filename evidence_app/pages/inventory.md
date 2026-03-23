---
title: Inventory
---
User Story & Minimum Viable Product:
- Track Product Movement
- Detect Restocking Events
- Inventory Updates

Use the filters below to answer the main KPI question: 
**Spot Stock Status** across stores, product groups, colours, size coverage, gender mix, and stock health.

```sql filter_stores
SELECT '' AS store_value, 'All stores' AS store_label
UNION ALL
SELECT DISTINCT
    store_name AS store_value,
    store_name AS store_label
FROM sportwear.query_1_jacket_inventory
ORDER BY store_label
```

```sql filter_products
SELECT '' AS category_value, 'All products' AS category_label
UNION ALL
SELECT DISTINCT
    category_name AS category_value,
    category_name AS category_label
FROM sportwear.data_products
WHERE category_name IS NOT NULL
ORDER BY category_label
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
    colour_name AS colour_value,
    colour_name AS colour_label
FROM sportwear.query_1_jacket_inventory
WHERE colour_name IS NOT NULL
ORDER BY colour_label
```

```sql filter_size_coverage
SELECT '' AS size_coverage_value, 'All size coverage' AS size_coverage_label
UNION ALL SELECT 'FULL_SIZE_COVERAGE', 'Full size coverage'
UNION ALL SELECT 'PARTIAL_SIZE_COVERAGE', 'Partial size coverage'
UNION ALL SELECT 'NO_SIZE_COVERAGE', 'No size coverage'
```

```sql filter_genders
SELECT '' AS gender_value, 'All genders' AS gender_label
UNION ALL SELECT 'Male', 'Male'
UNION ALL SELECT 'Female', 'Female'
UNION ALL SELECT 'Unisex', 'Unisex'
```

```sql filter_sizes
SELECT '' AS size_value, 'All sizes' AS size_label
UNION ALL SELECT 'XS', 'XS'
UNION ALL SELECT 'S', 'S'
UNION ALL SELECT 'M', 'M'
UNION ALL SELECT 'L', 'L'
UNION ALL SELECT 'XL', 'XL'
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
    value=category_value
    label=category_label
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

<div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
  <Dropdown
    data={filter_size_coverage}
    name="inventory_size_coverage"
    value=size_coverage_value
    label=size_coverage_label
    title="Size coverage"
  />
  <Dropdown
    data={filter_genders}
    name="inventory_gender"
    value=gender_value
    label=gender_label
    title="Gender"
  />
  <Dropdown
    data={filter_sizes}
    name="inventory_size"
    value=size_value
    label=size_label
    title="Size"
  />
</div>

```sql query_1_kpis
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
)
SELECT
    COUNT(DISTINCT category_name) AS product_groups,
    COUNT(DISTINCT product_name) AS products,
    COUNT(DISTINCT store_name) AS stores_covered,
    SUM(total_stock) AS total_units,
    SUM(CASE WHEN size_coverage_status = 'FULL_SIZE_COVERAGE' THEN 1 ELSE 0 END) AS full_size_rows,
    SUM(CASE WHEN stock_status = 'LOW_STOCK' THEN 1 ELSE 0 END) AS low_stock_rows,
    SUM(CASE WHEN stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) AS out_of_stock_rows,
    SUM(CASE WHEN stock_status = 'OK' THEN 1 ELSE 0 END) AS ok_stock_rows
FROM filtered_inventory
```

<BigValue data={query_1_kpis} value=total_units title="Total stock units" />

<Grid cols=4>
  <BigValue data={query_1_kpis} value=product_groups title="Product groups" />
  <BigValue data={query_1_kpis} value=products title="Products" />
  <BigValue data={query_1_kpis} value=stores_covered title="Stores covered" />
  <BigValue data={query_1_kpis} value=full_size_rows title="Full size coverage rows" />
</Grid>

<Grid cols=3>
  <BigValue data={query_1_kpis} value=low_stock_rows title="Low stock rows" />
  <BigValue data={query_1_kpis} value=out_of_stock_rows title="Out of stock rows" />
  <BigValue data={query_1_kpis} value=ok_stock_rows title="OK stock rows" />
</Grid>

```sql query_1_status_summary
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
)
SELECT
    CASE stock_status
        WHEN 'LOW_STOCK' THEN 'Low Stock'
        WHEN 'OUT_OF_STOCK' THEN 'Out of Stock'
        ELSE 'OK'
    END AS stock_status,
    COUNT(*) AS rows_in_status,
    SUM(total_stock) AS units_in_status
FROM filtered_inventory
GROUP BY 1
ORDER BY units_in_status DESC, stock_status
```

## Stock status summary

<BarChart data={query_1_status_summary} x=stock_status y=units_in_status title="Units by stock status" />

<DataTable data={query_1_status_summary} />

```sql query_1_all_stores
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
)
SELECT
    category_name,
    product_name,
    SUM(total_stock) AS total_stock,
    SUM(xs) AS xs,
    SUM(s) AS s,
    SUM(m) AS m,
    SUM(l) AS l,
    SUM(xl) AS xl,
    SUM(male) AS male,
    SUM(female) AS female,
    SUM(unisex) AS unisex,
    CASE
        WHEN SUM(total_stock) = 0 THEN 'Out of Stock'
        WHEN SUM(total_stock) < 10 THEN 'Low Stock'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN SUM(xs) > 0 AND SUM(s) > 0 AND SUM(m) > 0 AND SUM(l) > 0 AND SUM(xl) > 0 THEN 'Full size coverage'
        WHEN SUM(xs) > 0 OR SUM(s) > 0 OR SUM(m) > 0 OR SUM(l) > 0 OR SUM(xl) > 0 THEN 'Partial size coverage'
        ELSE 'No size coverage'
    END AS size_coverage_status
FROM filtered_inventory
GROUP BY category_name, product_name
ORDER BY total_stock DESC, category_name, product_name
```

## Current stock per product across all stores

<DataTable data={query_1_all_stores} />

```sql query_1_per_store
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
)
SELECT
    store_name,
    category_name,
    product_name,
    SUM(total_stock) AS total_stock,
    SUM(xs) AS xs,
    SUM(s) AS s,
    SUM(m) AS m,
    SUM(l) AS l,
    SUM(xl) AS xl,
    SUM(male) AS male,
    SUM(female) AS female,
    SUM(unisex) AS unisex,
    CASE
        WHEN SUM(total_stock) = 0 THEN 'Out of Stock'
        WHEN SUM(total_stock) < 10 THEN 'Low Stock'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN SUM(xs) > 0 AND SUM(s) > 0 AND SUM(m) > 0 AND SUM(l) > 0 AND SUM(xl) > 0 THEN 'Full size coverage'
        WHEN SUM(xs) > 0 OR SUM(s) > 0 OR SUM(m) > 0 OR SUM(l) > 0 OR SUM(xl) > 0 THEN 'Partial size coverage'
        ELSE 'No size coverage'
    END AS size_coverage_status
FROM filtered_inventory
GROUP BY store_name, category_name, product_name
ORDER BY store_name, total_stock DESC, product_name
```

## Smaller view per store

<DataTable data={query_1_per_store} />

```sql query_1_by_colour
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
)
SELECT
    store_name,
    category_name,
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
    CASE stock_status
        WHEN 'LOW_STOCK' THEN 'Low Stock'
        WHEN 'OUT_OF_STOCK' THEN 'Out of Stock'
        ELSE 'OK'
    END AS stock_status,
    CASE size_coverage_status
        WHEN 'FULL_SIZE_COVERAGE' THEN 'Full size coverage'
        WHEN 'PARTIAL_SIZE_COVERAGE' THEN 'Partial size coverage'
        ELSE 'No size coverage'
    END AS size_coverage_status
FROM filtered_inventory
ORDER BY category_name, store_name, product_name, total_stock DESC, colour_name
```

## By colour with stock status

<DataTable data={query_1_by_colour} />

<BarChart
  data={query_1_per_store}
  x=product_name
  y=total_stock
  series=store_name
  title="Stock by product and store"
/>

```sql query_1_stock_outliers
WITH product_categories AS (
    SELECT DISTINCT
        product_name,
        category_name
    FROM sportwear.data_products
    WHERE category_name IS NOT NULL
),
filtered_inventory AS (
    SELECT
        q.store_name,
        q.product_name,
        pc.category_name,
        q.colour_name,
        q.total_stock,
        q.xs,
        q.s,
        q.m,
        q.l,
        q.xl,
        q.male,
        q.female,
        q.unisex,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    LEFT JOIN product_categories pc
        ON q.product_name = pc.product_name
    WHERE ('${inputs.inventory_store.value}' = '' OR q.store_name = '${inputs.inventory_store.value}')
      AND ('${inputs.inventory_product.value}' = '' OR pc.category_name = '${inputs.inventory_product.value}')
      AND ('${inputs.inventory_stock_status.value}' = '' OR q.stock_status = '${inputs.inventory_stock_status.value}')
      AND ('${inputs.inventory_colour.value}' = '' OR q.colour_name = '${inputs.inventory_colour.value}')
      AND ('${inputs.inventory_size_coverage.value}' = '' OR q.size_coverage_status = '${inputs.inventory_size_coverage.value}')
      AND ('${inputs.inventory_gender.value}' = ''
           OR ('${inputs.inventory_gender.value}' = 'Male' AND q.male > 0)
           OR ('${inputs.inventory_gender.value}' = 'Female' AND q.female > 0)
           OR ('${inputs.inventory_gender.value}' = 'Unisex' AND q.unisex > 0))
      AND ('${inputs.inventory_size.value}' = ''
           OR ('${inputs.inventory_size.value}' = 'XS' AND q.xs > 0)
           OR ('${inputs.inventory_size.value}' = 'S' AND q.s > 0)
           OR ('${inputs.inventory_size.value}' = 'M' AND q.m > 0)
           OR ('${inputs.inventory_size.value}' = 'L' AND q.l > 0)
           OR ('${inputs.inventory_size.value}' = 'XL' AND q.xl > 0))
),
stock_base AS (
    SELECT
        store_name,
        category_name,
        product_name,
        SUM(total_stock) AS total_stock
    FROM filtered_inventory
    GROUP BY store_name, category_name, product_name
),
stock_stats AS (
    SELECT AVG(total_stock) AS avg_stock
    FROM stock_base
)
SELECT
    b.store_name,
    b.category_name,
    b.product_name,
    b.total_stock,
    ROUND(s.avg_stock, 2) AS average_stock,
    ROUND(b.total_stock - s.avg_stock, 2) AS stock_change_from_average,
    ROUND(ABS(b.total_stock - s.avg_stock), 2) AS absolute_change
FROM stock_base b
CROSS JOIN stock_stats s
ORDER BY absolute_change DESC, b.total_stock DESC, b.product_name
LIMIT 5
```

## Biggest outliers in stock level

This highlights the store-product combinations with the largest change versus the average stock level in the current filter selection.

<DataTable data={query_1_stock_outliers} />

<BarChart
  data={query_1_stock_outliers}
  x=product_name
  y=stock_change_from_average
  series=store_name
  title="Biggest stock outliers vs average"
/>
