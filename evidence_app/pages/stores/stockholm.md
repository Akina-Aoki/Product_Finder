---
title: Stockholm
---

# 🏬 Store Dashboard: Stockholm

This page gives managers a focused view of **Stockholm store performance** across sales and inventory health.
Use it to detect stock risk, monitor revenue, and prioritize restocking actions.

---

## Filters

```sql sthlm_sales_categories
SELECT '' AS category_value, 'All categories' AS category_label
UNION ALL
SELECT DISTINCT
    category_name AS category_value,
    category_name AS category_label
FROM sportwear.data_products
WHERE category_name IS NOT NULL
ORDER BY category_label
```

```sql sthlm_sales_products
SELECT '' AS product_value, 'All products' AS product_label
UNION ALL
SELECT DISTINCT
    product_name AS product_value,
    product_name AS product_label
FROM sportwear.data_products
WHERE product_name IS NOT NULL
  AND (
        '${inputs.sthlm_category.value}' = ''
        OR category_name = '${inputs.sthlm_category.value}'
      )
ORDER BY product_label
```

```sql sthlm_stock_status
SELECT '' AS stock_status_value, 'All stock statuses' AS stock_status_label
UNION ALL SELECT 'OK', 'OK'
UNION ALL SELECT 'LOW_STOCK', 'Low stock'
UNION ALL SELECT 'OUT_OF_STOCK', 'Out of stock'
```

<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
  <Dropdown data={sthlm_sales_categories} name="sthlm_category" value=category_value label=category_label title="Category" />
  <Dropdown data={sthlm_sales_products} name="sthlm_product" value=product_value label=product_label title="Product" />
  <Dropdown data={sthlm_stock_status} name="sthlm_status" value=stock_status_value label=stock_status_label title="Stock status" />
</div>

---

## Sales KPIs (Stockholm)

```sql sthlm_sales_kpis
WITH filtered_sales AS (
    SELECT
        s.order_id,
        s.order_date,
        s.product_id,
        s.quantity,
        s.item_price,
        p.product_name,
        p.category_name,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE LOWER(s.store_name) IN ('stockholm', 'sthlm')
      AND ('${inputs.sthlm_category.value}' = '' OR p.category_name = '${inputs.sthlm_category.value}')
      AND ('${inputs.sthlm_product.value}' = '' OR p.product_name = '${inputs.sthlm_product.value}')
)
SELECT
    COALESCE(SUM(revenue), 0) AS total_revenue_sek,
    COALESCE(SUM(quantity), 0) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT product_id) AS distinct_products,
    CASE
        WHEN COUNT(DISTINCT order_id) = 0 THEN 0
        ELSE ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2)
    END AS avg_order_value_sek
FROM filtered_sales
```

<Grid cols=5>
  <BigValue data={sthlm_sales_kpis} value=total_revenue_sek title="Revenue (SEK)" fmt=currency0 />
  <BigValue data={sthlm_sales_kpis} value=total_units_sold title="Units sold" />
  <BigValue data={sthlm_sales_kpis} value=total_orders title="Orders" />
  <BigValue data={sthlm_sales_kpis} value=distinct_products title="Products sold" />
  <BigValue data={sthlm_sales_kpis} value=avg_order_value_sek title="Avg. order value (SEK)" fmt=currency0 />
</Grid>

```sql sthlm_revenue_daily
WITH filtered_sales AS (
    SELECT
        CAST(order_date AS DATE) AS day,
        quantity * item_price AS revenue
    FROM sportwear.data_sales
    WHERE LOWER(store_name) IN ('stockholm', 'sthlm')
)
SELECT
    day,
    SUM(revenue) AS revenue_sek
FROM filtered_sales
GROUP BY day
ORDER BY day
```

<LineChart data={sthlm_revenue_daily} x=day y=revenue_sek title="Daily revenue trend (Stockholm)" />

---

## Inventory KPIs (Stockholm)

```sql sthlm_inventory_kpis
WITH filtered_inventory AS (
    SELECT
        q.product_name,
        q.category_name,
        q.total_stock,
        q.stock_status,
        q.size_coverage_status
    FROM sportwear.query_1_jacket_inventory q
    WHERE LOWER(q.store_name) IN ('stockholm', 'sthlm')
      AND ('${inputs.sthlm_category.value}' = '' OR q.category_name = '${inputs.sthlm_category.value}')
      AND ('${inputs.sthlm_product.value}' = '' OR q.product_name = '${inputs.sthlm_product.value}')
      AND ('${inputs.sthlm_status.value}' = '' OR q.stock_status = '${inputs.sthlm_status.value}')
)
SELECT
    COUNT(DISTINCT category_name) AS product_groups,
    COUNT(DISTINCT product_name) AS products,
    COALESCE(SUM(total_stock), 0) AS total_units,
    SUM(CASE WHEN stock_status = 'LOW_STOCK' THEN 1 ELSE 0 END) AS low_stock_rows,
    SUM(CASE WHEN stock_status = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) AS out_of_stock_rows,
    SUM(CASE WHEN size_coverage_status = 'FULL_SIZE_COVERAGE' THEN 1 ELSE 0 END) AS full_size_rows
FROM filtered_inventory
```

<Grid cols=3>
  <BigValue data={sthlm_inventory_kpis} value=total_units title="Total stock units" />
  <BigValue data={sthlm_inventory_kpis} value=low_stock_rows title="Low stock rows" />
  <BigValue data={sthlm_inventory_kpis} value=out_of_stock_rows title="Out of stock rows" />
</Grid>

<Grid cols=3>
  <BigValue data={sthlm_inventory_kpis} value=product_groups title="Product groups" />
  <BigValue data={sthlm_inventory_kpis} value=products title="Products" />
  <BigValue data={sthlm_inventory_kpis} value=full_size_rows title="Full size coverage rows" />
</Grid>

```sql sthlm_stock_status_chart
SELECT
    CASE stock_status
        WHEN 'LOW_STOCK' THEN 'Low stock'
        WHEN 'OUT_OF_STOCK' THEN 'Out of stock'
        ELSE 'OK'
    END AS stock_status_label,
    COUNT(*) AS rows_in_status,
    SUM(total_stock) AS units_in_status
FROM sportwear.query_1_jacket_inventory
WHERE LOWER(store_name) IN ('stockholm', 'sthlm')
GROUP BY 1
ORDER BY units_in_status DESC
```

<BarChart data={sthlm_stock_status_chart} x=stock_status_label y=units_in_status title="Units by stock status (Stockholm)" />

---

## Top products by revenue (Stockholm)

```sql sthlm_top_products_revenue
WITH filtered_sales AS (
    SELECT
        s.product_id,
        p.product_name,
        p.category_name,
        SUM(s.quantity) AS units_sold,
        SUM(s.quantity * s.item_price) AS total_revenue_sek
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE LOWER(s.store_name) IN ('stockholm', 'sthlm')
      AND ('${inputs.sthlm_category.value}' = '' OR p.category_name = '${inputs.sthlm_category.value}')
      AND ('${inputs.sthlm_product.value}' = '' OR p.product_name = '${inputs.sthlm_product.value}')
    GROUP BY s.product_id, p.product_name, p.category_name
)
SELECT *
FROM filtered_sales
ORDER BY total_revenue_sek DESC
LIMIT 15
```

<DataTable data={sthlm_top_products_revenue} />

## Low stock watchlist (Stockholm)

```sql sthlm_low_stock_watchlist
SELECT
    product_name,
    category_name,
    colour_name,
    total_stock,
    stock_status,
    size_coverage_status
FROM sportwear.query_1_jacket_inventory
WHERE LOWER(store_name) IN ('stockholm', 'sthlm')
  AND stock_status IN ('LOW_STOCK', 'OUT_OF_STOCK')
ORDER BY total_stock ASC, product_name
LIMIT 25
```

<DataTable data={sthlm_low_stock_watchlist} />