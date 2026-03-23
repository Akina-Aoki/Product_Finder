# Sales Performance Overview

MVP and user-story questions for sales:
- **Which products perform the best and worst?**
- **How strong is product revenue performance?**
- **How does revenue and sales move by day, week, and month?**

```sql filter_sales_stores
SELECT '' AS store_value, 'All stores' AS store_label
UNION ALL
SELECT DISTINCT
    store_name AS store_value,
    store_name AS store_label
FROM sportwear.query_2_sales
ORDER BY store_label
```

```sql filter_sales_categories
SELECT '' AS category_value, 'All categories' AS category_label
UNION ALL
SELECT DISTINCT
    category_name AS category_value,
    category_name AS category_label
FROM sportwear.query_2_sales
WHERE category_name IS NOT NULL
ORDER BY category_label
```

```sql filter_sales_products
SELECT '' AS product_value, 'All products' AS product_label
UNION ALL
SELECT DISTINCT
    product_name AS product_value,
    product_name AS product_label
FROM sportwear.query_2_sales
WHERE product_name IS NOT NULL
ORDER BY product_label
```

```sql filter_sales_cities
SELECT '' AS city_value, 'All cities' AS city_label
UNION ALL
SELECT DISTINCT
    city AS city_value,
    city AS city_label
FROM sportwear.query_2_sales
WHERE city IS NOT NULL
ORDER BY city_label
```

```sql filter_sales_genders
SELECT '' AS gender_value, 'All genders' AS gender_label
UNION ALL SELECT 'Male', 'Male'
UNION ALL SELECT 'Female', 'Female'
UNION ALL SELECT 'Unisex', 'Unisex'
```

<div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
  <Dropdown data={filter_sales_stores} name="sales_store" value=store_value label=store_label title="Store" />
  <Dropdown data={filter_sales_categories} name="sales_category" value=category_value label=category_label title="Category" />
  <Dropdown data={filter_sales_products} name="sales_product" value=product_value label=product_label title="Product" />
</div>

<div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
  <Dropdown data={filter_sales_cities} name="sales_city" value=city_value label=city_label title="City" />
  <Dropdown data={filter_sales_genders} name="sales_gender" value=gender_value label=gender_label title="Gender" />
</div>

## Selected filters

<div style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px;">
  <div><strong>Store:</strong> {inputs.sales_store.value || 'All stores'}</div>
  <div><strong>Category:</strong> {inputs.sales_category.value || 'All categories'}</div>
  <div><strong>Product:</strong> {inputs.sales_product.value || 'All products'}</div>
  <div><strong>City:</strong> {inputs.sales_city.value || 'All cities'}</div>
  <div><strong>Gender:</strong> {inputs.sales_gender.value || 'All genders'}</div>
</div>


```sql sales_kpis
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    SUM(line_revenue) AS total_revenue_sek,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT product_name) AS distinct_products,
    ROUND(SUM(line_revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS avg_order_value_sek
FROM filtered_sales
```

<Grid cols=5>
  <BigValue data={sales_kpis} value=total_revenue_sek title="Total revenue (SEK)" />
  <BigValue data={sales_kpis} value=total_units_sold title="Units sold" />
  <BigValue data={sales_kpis} value=total_orders title="Orders" />
  <BigValue data={sales_kpis} value=distinct_products title="Products sold" />
  <BigValue data={sales_kpis} value=avg_order_value_sek title="Avg. order value (SEK)" />
</Grid>

```sql product_revenue_ranking
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
),
product_summary AS (
    SELECT
        category_name,
        product_name,
        SUM(quantity) AS units_sold,
        SUM(line_revenue) AS total_revenue_sek,
        COUNT(DISTINCT order_id) AS orders_count
    FROM filtered_sales
    GROUP BY category_name, product_name
)
SELECT
    category_name,
    product_name,
    units_sold,
    orders_count,
    total_revenue_sek,
    DENSE_RANK() OVER (ORDER BY total_revenue_sek DESC) AS revenue_rank_desc,
    DENSE_RANK() OVER (ORDER BY total_revenue_sek ASC) AS revenue_rank_asc
FROM product_summary
ORDER BY total_revenue_sek DESC, product_name
```

## Revenue performance by product

<DataTable data={product_revenue_ranking} groupBy=category_name subtotals=true totalRow=true>
  <Column id=category_name title="Category" totalAgg=Total />
  <Column id=product_name title="Product" totalAgg=countDistinct totalFmt='0 "products"' />
  <Column id=units_sold title="Units sold" contentType=colorscale totalAgg=sum />
  <Column id=orders_count title="Orders" contentType=colorscale totalAgg=sum />
  <Column id=total_revenue_sek title="Revenue (SEK)" contentType=bar barColor=#aecfaf backgroundColor=#ebebeb totalAgg=sum />
  <Column id=revenue_rank_desc title="Best rank" />
  <Column id=revenue_rank_asc title="Worst rank" />
</DataTable>

```sql top_performing_products
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    category_name,
    product_name,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders_count,
    SUM(line_revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY category_name, product_name
ORDER BY total_revenue_sek DESC, units_sold DESC, product_name
LIMIT 10
```

```sql lowest_performing_products
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    category_name,
    product_name,
    SUM(quantity) AS units_sold,
    COUNT(DISTINCT order_id) AS orders_count,
    SUM(line_revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY category_name, product_name
ORDER BY total_revenue_sek ASC, units_sold ASC, product_name
LIMIT 10
```

<Grid cols=2>
  <div>
    <h2>Highest performing products</h2>
    <DataTable data={top_performing_products}>
      <Column id=category_name title="Category" />
      <Column id=product_name title="Product" />
      <Column id=units_sold title="Units sold" contentType=colorscale />
      <Column id=orders_count title="Orders" contentType=colorscale />
      <Column id=total_revenue_sek title="Revenue (SEK)" contentType=bar barColor=#aecfaf backgroundColor=#ebebeb />
    </DataTable>
  </div>
  <div>
    <h2>Lowest performing products</h2>
    <DataTable data={lowest_performing_products}>
      <Column id=category_name title="Category" />
      <Column id=product_name title="Product" />
      <Column id=units_sold title="Units sold" contentType=colorscale />
      <Column id=orders_count title="Orders" contentType=colorscale />
      <Column id=total_revenue_sek title="Revenue (SEK)" contentType=bar barColor=#ffe08a backgroundColor=#ebebeb />
    </DataTable>
  </div>
</Grid>

```sql revenue_daily_summary
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    order_day,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(line_revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY order_day
ORDER BY order_day
```

```sql revenue_weekly_summary
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    order_week,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(line_revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY order_week
ORDER BY order_week
```

```sql revenue_monthly_summary
WITH filtered_sales AS (
    SELECT *
    FROM sportwear.query_2_sales
    WHERE ('${inputs.sales_store.value}' = '' OR store_name = '${inputs.sales_store.value}')
      AND ('${inputs.sales_category.value}' = '' OR category_name = '${inputs.sales_category.value}')
      AND ('${inputs.sales_product.value}' = '' OR product_name = '${inputs.sales_product.value}')
      AND ('${inputs.sales_city.value}' = '' OR city = '${inputs.sales_city.value}')
      AND ('${inputs.sales_gender.value}' = '' OR gender_name = '${inputs.sales_gender.value}')
)
SELECT
    order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(line_revenue) AS total_revenue_sek
FROM filtered_sales
GROUP BY order_month
ORDER BY order_month
```

## Daily revenue and sales

<LineChart data={revenue_daily_summary} x=order_day y=total_revenue_sek title="Daily revenue" />
<DataTable data={revenue_daily_summary} />

## Weekly revenue and sales

<LineChart data={revenue_weekly_summary} x=order_week y=total_revenue_sek title="Weekly revenue" />
<DataTable data={revenue_weekly_summary} />

## Monthly revenue and sales

<BarChart data={revenue_monthly_summary} x=order_month y=total_revenue_sek title="Monthly revenue" />
<DataTable data={revenue_monthly_summary} />