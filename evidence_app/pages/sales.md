# Sales Performance Overview

MVP and user-story questions for sales:

* **Which products perform the best and worst?**
* **How strong is product revenue performance?**
* **How does revenue and sales move by day, week, and month?**

---

## Filters

```sql filter_sales_stores
SELECT DISTINCT store_name AS store_value, store_name AS store_label
FROM sportwear.data_sales
ORDER BY store_label
```

```sql filter_sales_categories
SELECT DISTINCT category_name AS category_value, category_name AS category_label
FROM sportwear.data_products
WHERE category_name IS NOT NULL
ORDER BY category_label
```


```sql filter_sales_products 
SELECT DISTINCT product_name AS product_value, product_name AS product_label
FROM sportwear.data_products
WHERE product_name IS NOT NULL
  AND category_name LIKE '${inputs.sales_category.value}'
ORDER BY product_label
```


```sql filter_sales_genders
SELECT DISTINCT gender_name AS gender_value, gender_name AS gender_label
FROM sportwear.data_products
WHERE gender_name IS NOT NULL
ORDER BY gender_label
```


```sql filter_sales_sizes
SELECT DISTINCT size_name AS size_value, size_name AS size_label
FROM sportwear.data_products
WHERE size_name IS NOT NULL
ORDER BY size_label
```

```sql filter_sales_colors
SELECT DISTINCT colour_name AS color_value, colour_name AS color_label
FROM sportwear.data_products
WHERE colour_name IS NOT NULL
ORDER BY color_label
```

```sql filter_sales_week
SELECT DISTINCT 
    DATE_TRUNC('week', DATE(order_date)) AS week_value,
    DATE_TRUNC('week', DATE(order_date)) AS week_label
FROM sportwear.data_sales
ORDER BY week_label DESC
```

---

<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
  <Dropdown data={filter_sales_stores} name="sales_store" value=store_value label=store_label title="Store">
    <DropdownOption value="%" valueLabel="All Stores" />
  </Dropdown>
  <Dropdown data={filter_sales_categories} name="sales_category" value=category_value label=category_label title="Category">
    <DropdownOption value="%" valueLabel="All Categories" />
  </Dropdown>
  <Dropdown data={filter_sales_products} name="sales_product" value=product_value label=product_label title="Product">
    <DropdownOption value="%" valueLabel="All Products" />
  </Dropdown>
  <Dropdown data={filter_sales_genders} name="sales_gender" value=gender_value label=gender_label title="Gender">
    <DropdownOption value="%" valueLabel="All Genders" />
  </Dropdown>
  <Dropdown data={filter_sales_sizes} name="sales_size" value=size_value label=size_label title="Size">
    <DropdownOption value="%" valueLabel="All Sizes" />
  </Dropdown>
  <Dropdown data={filter_sales_colors} name="sales_color" value=color_value label=color_label title="Color">
    <DropdownOption value="%" valueLabel="All Colors" />
  </Dropdown>
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
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
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
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
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
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
),
inventory_summary AS (
    SELECT
        product AS product_name,
        SUM(COALESCE(amount, 0)) AS current_stock,
        CASE
            WHEN SUM(COALESCE(amount, 0)) = 0 THEN 'Out of Stock'
            WHEN SUM(COALESCE(amount, 0)) < 10 THEN 'Low Stock'
            ELSE 'OK'
        END AS stock_status
    FROM sportwear.data_inventories
    WHERE store_name LIKE '${inputs.sales_store.value}'
      AND category LIKE '${inputs.sales_category.value}'
      AND product LIKE '${inputs.sales_product.value}'
      AND gender LIKE '${inputs.sales_gender.value}'
      AND size LIKE '${inputs.sales_size.value}'
      AND colour LIKE '${inputs.sales_color.value}'
    GROUP BY product
)
SELECT
    fs.category_name,
    fs.product_name,
    SUM(fs.quantity) AS units_sold,
    SUM(fs.revenue) AS total_revenue_sek,
    COALESCE(i.current_stock, 0) AS current_stock,
    COALESCE(i.stock_status, 'Unknown') AS stock_status
FROM filtered_sales fs
LEFT JOIN inventory_summary i
    ON fs.product_name = i.product_name
GROUP BY fs.category_name, fs.product_name, i.current_stock, i.stock_status
ORDER BY total_revenue_sek DESC
```

<DataTable data={product_revenue}>
    <Column id=category_name title="Category" />
    <Column id=product_name title="Product" />
    <Column id=units_sold title="Units Sold" />
    <Column id=total_revenue_sek title="Revenue (SEK)" contentType=bar />
    <Column id=current_stock title="Current Stock" />
    <Column id=stock_status title="Stock Status" />
</DataTable>
---

# Daily Revenue


```sql revenue_daily_1
WITH filtered_sales AS (
    SELECT
        CAST(s.order_date AS DATE) AS day,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
),

daily AS (
    SELECT
        day,
        SUM(revenue) AS revenue_sek
    FROM filtered_sales
    GROUP BY day
)

SELECT
    day,
    revenue_sek,

    revenue_sek - LAG(revenue_sek) OVER (
        ORDER BY day
    ) AS revenue_change

FROM daily
ORDER BY day DESC
LIMIT 30
```


<DataTable data={revenue_daily_1}>
    <Column id=day title="Date" />
    <Column id=revenue_sek title="Revenue (SEK)" />
    <Column 
        id=revenue_change 
        title="Change" 
        contentType=delta 
        fmt=currency0 
    />
</DataTable>

----

```sql revenue_daily_2
WITH base AS (
    SELECT
        DATE(s.order_date) AS day,
        p.category_name,
        p.product_name,
        s.quantity,
        s.item_price,
        s.quantity * s.item_price AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
),

aggregated AS (
    SELECT
        day,
        category_name,
        product_name,
        SUM(quantity) AS units,
        SUM(revenue) AS revenue
    FROM base
    GROUP BY day, category_name, product_name
),

with_growth AS (
    SELECT
        *,
        revenue - LAG(revenue) OVER (
            PARTITION BY product_name
            ORDER BY day
        ) AS revenue_change
    FROM aggregated
)

SELECT *
FROM with_growth
ORDER BY day DESC, revenue DESC
LIMIT 100
```


<DataTable 
  data={revenue_daily_2} 
  groupBy=category_name 
  subtotals=true 
  totalRow=true
>
  <Column id=category_name title="Category" totalAgg="Total"/>
  <Column id=product_name title="Product"/>
  <Column id=day title="Date"/>
  
  <Column 
    id=units 
    title="Units" 
    contentType=colorscale 
  />

  <Column 
    id=revenue 
    title="Revenue (SEK)" 
    contentType=bar 
  />

  <Column 
    id=revenue_change 
    title="Growth" 
    contentType=delta 
    fmt=currency0 
  />
</DataTable>

----

# Weekly Revenue


```sql revenue_weekly
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
),

weekly AS (
    SELECT
        DATE_TRUNC('week', DATE(order_date)) AS week_start,
        SUM(revenue) AS revenue_sek
    FROM filtered_sales
    GROUP BY week_start
)

SELECT
    week_start,
    revenue_sek,

    -- 🔥 smooth trend (VERY important)
    AVG(revenue_sek) OVER (
        ORDER BY week_start
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS revenue_trend

FROM weekly
ORDER BY week_start
```

**Revenue Sek = This is the actual weekly revenue** <br>
**Revenue Trend = This is a rolling average of revenue**<br>

<LineChart 
  data={revenue_weekly} 
  x=week_start 
  y=revenue_sek 
  y2=revenue_trend
  title="Weekly Revenue Trend"
/>

---

```sql revenue_weekly_detailed

WITH filtered_sales AS (
    SELECT
        DATE_TRUNC('week', DATE(s.order_date)) AS week_start,
        p.category_name,
        p.product_name,
        SUM(s.quantity) AS units,
        SUM(s.quantity * s.item_price) AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
    GROUP BY 1,2,3
),

with_growth AS (
    SELECT
        *,
        revenue - LAG(revenue) OVER (
            PARTITION BY product_name
            ORDER BY week_start
        ) AS revenue_change
    FROM filtered_sales
)

SELECT
    category_name,
    product_name,
    week_start,
    units,
    revenue,
    revenue_change
FROM with_growth
ORDER BY week_start DESC, revenue DESC

```


<DataTable 
  data={revenue_weekly_detailed} 
  groupBy=category_name 
  subtotals=true 
  totalRow=true
>
  <Column id=category_name title="Category" totalAgg="Total"/>
  <Column id=product_name title="Product"/>
  <Column id=week_start title="Week"/>
  <Column id=units title="Units" contentType=colorscale />
  <Column id=revenue title="Revenue (SEK)" contentType=bar />
  <Column 
    id=revenue_change 
    title="Growth" 
    contentType=delta 
    fmt=currency0 
  />
</DataTable>



----

# Monthly Revenue


```sql revenue_monthly
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
),

monthly AS (
    SELECT
        DATE_TRUNC('month', DATE(order_date)) AS month_start,
        SUM(revenue) AS revenue_sek
    FROM filtered_sales
    GROUP BY month_start
)

SELECT
    month_start,
    revenue_sek,

    -- existing change
    revenue_sek - LAG(revenue_sek) OVER (
        ORDER BY month_start
    ) AS revenue_change,

    -- 🔥 NEW: smoothed trend (3-month rolling)
    AVG(revenue_sek) OVER (
        ORDER BY month_start
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS revenue_trend

FROM monthly
ORDER BY month_start
```

<LineChart 
  data={revenue_monthly} 
  x=month_start 
  y=revenue_sek 
  y2=revenue_trend
  title="Monthly Revenue Trend"
/>

<DataTable data={revenue_monthly} totalRow=true>
  <Column id=month_start title="Month" totalAgg="Total"/>
  <Column id=revenue_sek title="Revenue (SEK)" contentType=bar/>
  <Column id=revenue_change title="Growth" contentType=delta fmt=currency0/>
  <Column id=revenue_trend title="Trend" contentType=colorscale/>
</DataTable>

----

# Yearly Revenue


```sql revenue_yearly_1
WITH filtered_sales AS (
    SELECT
        s.order_date,
        s.quantity * s.item_price AS revenue,
        p.category_name
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'
)

SELECT
    year_start,
    revenue_sek,

    -- 🔥 growth vs previous year
    revenue_sek - LAG(revenue_sek) OVER (
        ORDER BY year_start
    ) AS revenue_change

FROM (
    SELECT
        DATE_TRUNC('year', DATE(order_date)) AS year_start,
        SUM(revenue) AS revenue_sek
    FROM filtered_sales
    GROUP BY year_start
) yearly
ORDER BY year_start
```

<DataTable data={revenue_yearly_1}>
  <Column id=year_start title="Year"/>
  <Column id=revenue_sek title="Revenue (SEK)" contentType=bar/>
  <Column id=revenue_change title="Growth" contentType=delta fmt=currency0/>
</DataTable>



<BarChart data={revenue_yearly_1} x=year_start y=revenue_sek title="Yearly Revenue" />


----



```sql revenue_yearly_2
WITH filtered_sales AS (
    SELECT
        DATE_TRUNC('year', DATE(s.order_date)) AS year_start,
        p.category_name,
        p.product_name,
        SUM(s.quantity) AS units,
        SUM(s.quantity * s.item_price) AS revenue
    FROM sportwear.data_sales s
    LEFT JOIN sportwear.data_products p
        ON s.product_id = p.product_id
    WHERE s.store_name LIKE '${inputs.sales_store.value}'
        AND p.category_name LIKE '${inputs.sales_category.value}'
        AND p.product_name LIKE '${inputs.sales_product.value}'
        AND p.gender_name LIKE '${inputs.sales_gender.value}'
        AND p.size_name LIKE '${inputs.sales_size.value}'
        AND p.colour_name LIKE '${inputs.sales_color.value}'    GROUP BY 1,2,3
),

with_growth AS (
    SELECT
        *,
        revenue - LAG(revenue) OVER (
            PARTITION BY product_name
            ORDER BY year_start
        ) AS revenue_change
    FROM filtered_sales
)

SELECT
    category_name,
    product_name,
    year_start,
    units,
    revenue,
    revenue_change
FROM with_growth
ORDER BY year_start DESC, revenue DESC
```

<DataTable 
  data={revenue_yearly_2} 
  groupBy=category_name 
  subtotals=true 
  totalRow=true
>
  <Column id=category_name title="Category" totalAgg="Total"/>
  <Column id=product_name title="Product"/>
  <Column id=year_start title="Year"/>
  <Column id=units title="Units" contentType=colorscale />
  <Column id=revenue title="Revenue (SEK)" contentType=bar />
  <Column 
    id=revenue_change 
    title="Growth" 
    contentType=delta 
    fmt=currency0 
  />
</DataTable>