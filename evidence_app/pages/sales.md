# Sales Performance Overview

MVP and user-story questions for sales:

* **Which products perform the best and worst?**
* **How strong is product revenue performance?**
* **How does revenue and sales move by day, week, and month?**

---

## Filters

```sql filter_sales_stores
SELECT '' AS store_value, 'All stores' AS store_label
UNION ALL
SELECT DISTINCT
    store_name AS store_value,
    store_name AS store_label
FROM sportwear.data_sales
ORDER BY store_label
```

```sql filter_sales_categories
SELECT '' AS category_value, 'All categories' AS category_label
UNION ALL
SELECT DISTINCT
    category_name AS category_value,
    category_name AS category_label
FROM sportwear.data_products
WHERE category_name IS NOT NULL
ORDER BY category_label
```


```sql filter_sales_products 
SELECT '' AS product_value, 'All products' AS product_label
UNION ALL
SELECT DISTINCT
    product_name AS product_value,
    product_name AS product_label
FROM sportwear.data_products
WHERE product_name IS NOT NULL
  AND (
        '${inputs.sales_category.value}' = ''
        OR category_name = '${inputs.sales_category.value}'
      )
ORDER BY product_label
```


```sql filter_sales_genders
SELECT '' AS gender_value, 'All genders' AS gender_label
UNION ALL
SELECT DISTINCT
    gender_name AS gender_value,
    gender_name AS gender_label
FROM sportwear.data_products
WHERE gender_name IS NOT NULL
ORDER BY gender_label
```


```sql filter_sales_sizes
SELECT '' AS size_value, 'All sizes' AS size_label
UNION ALL
SELECT DISTINCT
    size_name AS size_value,
    size_name AS size_label
FROM sportwear.data_products
WHERE size_name IS NOT NULL
ORDER BY size_label
```

```sql filter_sales_colors
SELECT '' AS color_value, 'All colors' AS color_label
UNION ALL
SELECT DISTINCT
    colour_name AS color_value,
    colour_name AS color_label
FROM sportwear.data_products
WHERE colour_name IS NOT NULL
ORDER BY color_label
```


---

<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
  <Dropdown data={filter_sales_stores} name="sales_store" value=store_value label=store_label title="Store" />
  <Dropdown data={filter_sales_categories} name="sales_category" value=category_value label=category_label title="Category" />
  <Dropdown data={filter_sales_products} name="sales_product" value=product_value label=product_label title="Product" />
  <Dropdown data={filter_sales_genders} name="sales_gender" value=gender_value label=gender_label title="Gender" />
  <Dropdown data={filter_sales_sizes} name="sales_size" value=size_value label=size_label title="Size" />
  <Dropdown data={filter_sales_colors} name="sales_color" value=color_value label=color_label title="Color" />
</div>

---

## KPIs

```sql sales_kpis
WITH filtered_sales AS (
    SELECT
        s.order_id,
        s.order_date,
        s.store_name,
        s.product_id,
        s.quantity,
        s.item_price,
        p.product_name,
        p.category_name,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR p.product_name = '${inputs.sales_product.value}')
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
  <BigValue data={sales_kpis} value=total_revenue_sek title="Total revenue (SEK)" fmt=currency0 />
  <BigValue data={sales_kpis} value=total_units_sold title="Units sold" />
  <BigValue data={sales_kpis} value=total_orders title="Orders" />
  <BigValue data={sales_kpis} value=distinct_products title="Products sold" />
  <BigValue data={sales_kpis} value=avg_order_value_sek title="Avg. order value (SEK)" fmt=currency0 />
</Grid>

```sql sales_time_kpis
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.store_name,
        s.product_id,
        s.quantity,
        s.item_price,
        p.category_name,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
)
SELECT
    COALESCE(SUM(CASE WHEN CAST(order_date AS DATE) = CURRENT_DATE THEN revenue END), 0) AS revenue_today_sek,
    COALESCE(SUM(CASE WHEN DATE_TRUNC('week', order_date) = DATE_TRUNC('week', CURRENT_DATE) THEN revenue END), 0) AS revenue_week_sek,
    COALESCE(SUM(CASE WHEN DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE) THEN revenue END), 0) AS revenue_month_sek,
    COALESCE(SUM(CASE WHEN DATE_TRUNC('year', order_date) = DATE_TRUNC('year', CURRENT_DATE) THEN revenue END), 0) AS revenue_year_sek
FROM filtered_sales
```

<Grid cols=4>
  <BigValue data={sales_time_kpis} value=revenue_today_sek title="Revenue today (SEK)" fmt=currency0 />
  <BigValue data={sales_time_kpis} value=revenue_week_sek title="Revenue this week (SEK)" fmt=currency0 />
  <BigValue data={sales_time_kpis} value=revenue_month_sek title="Revenue this month (SEK)" fmt=currency0 />
  <BigValue data={sales_time_kpis} value=revenue_year_sek title="Revenue this year (SEK)" fmt=currency0 />
</Grid>

---

## Revenue by product

```sql product_revenue
WITH filtered_sales AS (
    SELECT
        s.product_id,
        s.quantity,
        s.item_price,
        p.product_name,
        p.category_name,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
)
SELECT
    category_name,
    product_name,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY category_name, product_name
ORDER BY total_revenue_sek DESC
```

<DataTable data={product_revenue}>
    <Column id=category_name title="Category" />
    <Column id=product_name title="Product" />
    <Column id=total_revenue_sek title="Revenue (SEK)" contentType=bar />
    <Column id=total_revenue_sek title="Revenue" contentType=bar barColor=#aecfaf/>
    <Column id=total_revenue_sek title="Revenue" contentType=bar barColor=#ffe08a backgroundColor=#ebebeb/>
</DataTable>
---

## Revenue Trends

```sql revenue_daily
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
)
SELECT
    CAST(order_date AS DATE) AS day,
    SUM(revenue) AS revenue_sek
FROM filtered_sales
GROUP BY day
ORDER BY day
```

<LineChart data={revenue_daily} x=day y=revenue_sek title = "Daily Revenue" />


```sql revenue_weekly
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
)
SELECT
    DATE_TRUNC('week', CAST(order_date AS DATE)) AS week_start,
    SUM(revenue) AS revenue_sek
FROM filtered_sales
GROUP BY week_start
ORDER BY week_start
```

<LineChart data={revenue_weekly} x=week_start y=revenue_sek title="Weekly revenue" />

```sql revenue_monthly
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE ('${inputs.sales_store.value}' = '' OR s.store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR p.category_name = '${inputs.sales_category.value}')
)
SELECT
    DATE_TRUNC('month', CAST(order_date AS DATE)) AS month_start,
    SUM(revenue) AS revenue_sek
FROM filtered_sales
GROUP BY month_start
ORDER BY month_start
```

<LineChart data={revenue_monthly} x=month_start y=revenue_sek title="Monthly revenue" />
