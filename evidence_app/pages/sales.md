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
FROM sportwear.data_sales
ORDER BY category_label
```

```sql filter_sales_products
SELECT '' AS product_value, 'All products' AS product_label
UNION ALL
SELECT DISTINCT
    product_name AS product_value,
    product_name AS product_label
FROM sportwear.data_sales
ORDER BY product_label
```

```sql filter_sales_cities
SELECT '' AS city_value, 'All cities' AS city_label
UNION ALL
SELECT DISTINCT
    city AS city_value,
    city AS city_label
FROM sportwear.data_sales
ORDER BY city_label
```

```sql filter_sales_genders
SELECT '' AS gender_value, 'All genders' AS gender_label
UNION ALL SELECT 'Male', 'Male'
UNION ALL SELECT 'Female', 'Female'
UNION ALL SELECT 'Unisex', 'Unisex'
```

---

<div style="display: flex; gap: 20px; flex-wrap: wrap;">
  <Dropdown data={filter_sales_stores} name="sales_store" value=store_value label=store_label title="Store" />
  <Dropdown data={filter_sales_categories} name="sales_category" value=category_value label=category_label title="Category" />
  <Dropdown data={filter_sales_products} name="sales_product" value=product_value label=product_label title="Product" />
</div>

<div style="display: flex; gap: 20px; flex-wrap: wrap;">
  <Dropdown data={filter_sales_cities} name="sales_city" value=city_value label=city_label title="City" />
  <Dropdown data={filter_sales_genders} name="sales_gender" value=gender_value label=gender_label title="Gender" />
</div>

---

## KPIs

```sql sales_kpis
SELECT COUNT(*) FROM sportwear.data_sales;
```

<Grid cols=5>
  <BigValue data={sales_kpis} value=total_revenue_sek title="Total revenue (SEK)" />
  <BigValue data={sales_kpis} value=total_units_sold title="Units sold" />
  <BigValue data={sales_kpis} value=total_orders title="Orders" />
  <BigValue data={sales_kpis} value=distinct_products title="Products sold" />
  <BigValue data={sales_kpis} value=avg_order_value_sek title="Avg. order value (SEK)" />
</Grid>

---

## Revenue by product

```sql product_revenue
WITH product_attributes AS (
    SELECT
        product_id,
        MAX(category_name) AS category_name
    FROM sportwear.data_sales
    GROUP BY product_id
),

sales_base AS (
    SELECT
        s.product_name,
        pa.category_name,
        s.quantity,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN product_attributes pa
        ON s.product_id = pa.product_id
)

SELECT
    category_name,
    product_name,
    SUM(quantity) AS units_sold,
    SUM(revenue) AS total_revenue
FROM sales_base
GROUP BY category_name, product_name
ORDER BY total_revenue DESC
```

<DataTable data={product_revenue} />

---

## Daily revenue

```sql revenue_daily
SELECT
    DATE(order_date) AS day,
    SUM(quantity * item_price) AS revenue
FROM sportwear.data_sales
GROUP BY day
ORDER BY day
```

<LineChart data={revenue_daily} x=day y=revenue />

---
