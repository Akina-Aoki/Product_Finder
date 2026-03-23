-- Must register it as a VIEW in Postgres for the sales dashboard to materialze in the DB

/*
CREATE SCHEMA IF NOT EXISTS sportwear;

CREATE OR REPLACE VIEW sportwear.query_2_sales AS
WITH product_attributes AS (
    SELECT DISTINCT
        product_id,
        category_name,
        colour_name,
        size_name,
        gender_name
    FROM refined.products
)
SELECT
    s.item_id,
    s.order_id,
    s.order_date,
    DATE(s.order_date) AS order_day,
    DATE_TRUNC('week', s.order_date)::DATE AS order_week,
    DATE_TRUNC('month', s.order_date)::DATE AS order_month,
    s.store_name,
    s.city,
    s.product_id,
    s.product_name,
    pa.category_name,
    pa.colour_name,
    pa.size_name,
    pa.gender_name,
    s.quantity,
    s.item_price,
    s.quantity * s.item_price AS line_revenue
FROM refined.items s
LEFT JOIN product_attributes pa
    ON s.product_id = pa.product_id;
*/

-- SELECT * FROM sportwear.query_2_sales LIMIT 10;



CREATE SCHEMA IF NOT EXISTS sportwear;

CREATE OR REPLACE VIEW sportwear.query_2_sales AS
SELECT
        i.item_id,
    i.order_id,
    i.order_date,
    DATE(i.order_date) AS order_day,
    DATE_TRUNC('week', i.order_date)::DATE AS order_week,
    DATE_TRUNC('month', i.order_date)::DATE AS order_month,
    i.store_name,
    i.city,
    i.product_id,
    i.product_name,
    p.category_name,
    p.colour_name,
    p.size_name,
    p.gender_name,
    i.quantity,
    i.item_price,
    i.quantity * i.item_price AS revenue
FROM refined.items i
LEFT JOIN refined.products p
    ON i.product_id = p.product_id;

SELECT * FROM sportwear.query_2_sales LIMIT 10;