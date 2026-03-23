---
title: Inventory
---

# Company Inventory Overview

What is the current status of our inventory warehouse?
Is this product in out of stock, low stock or OK in stock level status?

```sql filter_stores
SELECT DISTINCT
    store_name
FROM sportwear.query_1_jacket_inventory
ORDER BY store_name
```

<div style="display: flex; gap: 20px; margin-bottom: 20px;">
  <Dropdown
    data={filter_stores}
    name="inventory_store"
    value=store_name
    label=store_name
    selectAll="true"
  />
</div>

```sql query_1_kpis
SELECT
    COUNT(DISTINCT product_name) AS jacket_products,
    COUNT(DISTINCT store_name) AS stores_covered,
    SUM(total_stock) AS total_units,
    SUM(CASE WHEN size_coverage_status = 'FULL_SIZE_COVERAGE' THEN 1 ELSE 0 END) AS full_size_rows,
    SUM(CASE WHEN stock_status = 'LOW_STOCK' THEN 1 ELSE 0 END) AS low_stock_rows,
    SUM(CASE WHEN stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) AS out_of_stock_rows
FROM sportwear.query_1_jacket_inventory
WHERE ('${inputs.inventory_store.value}' = 'true' OR '${inputs.inventory_store.value}' = '')
   OR store_name = '${inputs.inventory_store.value}'
```

<BigValue
  data={query_1_kpis}
  value=total_units
  title="Total jacket stock"
/>

<Grid cols=3>
  <BigValue data={query_1_kpis} value=jacket_products title="Products" />
  <BigValue data={query_1_kpis} value=full_size_rows title="Full size coverage rows" />
  <BigValue data={query_1_kpis} value=low_stock_rows title="Low stock rows" />
</Grid>

```sql query_1_all_stores
SELECT
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
        WHEN SUM(total_stock) = 0 THEN 'OUT_OF_STOCK'
        WHEN SUM(total_stock) < 10 THEN 'LOW_STOCK'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN SUM(xs) > 0 AND SUM(s) > 0 AND SUM(m) > 0 AND SUM(l) > 0 AND SUM(xl) > 0 THEN 'FULL_SIZE_COVERAGE'
        WHEN SUM(xs) > 0 OR SUM(s) > 0 OR SUM(m) > 0 OR SUM(l) > 0 OR SUM(xl) > 0 THEN 'PARTIAL_SIZE_COVERAGE'
        ELSE 'NO_SIZE_COVERAGE'
    END AS size_coverage_status
FROM sportwear.query_1_jacket_inventory
GROUP BY product_name
ORDER BY total_stock DESC, product_name
```

## Current stock per product across all stores

<DataTable data={query_1_all_stores} />

```sql query_1_per_store
SELECT
    store_name,
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
        WHEN SUM(total_stock) = 0 THEN 'OUT_OF_STOCK'
        WHEN SUM(total_stock) < 10 THEN 'LOW_STOCK'
        ELSE 'OK'
    END AS stock_status,
    CASE
        WHEN SUM(xs) > 0 AND SUM(s) > 0 AND SUM(m) > 0 AND SUM(l) > 0 AND SUM(xl) > 0 THEN 'FULL_SIZE_COVERAGE'
        WHEN SUM(xs) > 0 OR SUM(s) > 0 OR SUM(m) > 0 OR SUM(l) > 0 OR SUM(xl) > 0 THEN 'PARTIAL_SIZE_COVERAGE'
        ELSE 'NO_SIZE_COVERAGE'
    END AS size_coverage_status
FROM sportwear.query_1_jacket_inventory
WHERE ('${inputs.inventory_store.value}' = 'true' OR '${inputs.inventory_store.value}' = '')
   OR store_name = '${inputs.inventory_store.value}'
GROUP BY store_name, product_name
ORDER BY store_name, total_stock DESC, product_name
```

## Smaller view per store

<DataTable data={query_1_per_store} />

```sql query_1_by_colour
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
    stock_status,
    size_coverage_status
FROM sportwear.query_1_jacket_inventory
WHERE ('${inputs.inventory_store.value}' = 'true' OR '${inputs.inventory_store.value}' = '')
   OR store_name = '${inputs.inventory_store.value}'
ORDER BY store_name, product_name, total_stock DESC, colour_name
```

## By colour with stock status

<DataTable data={query_1_by_colour} />

<BarChart
  data={query_1_per_store}
  x=product_name
  y=total_stock
  series=store_name
  title="Jacket stock by product and store"
/>