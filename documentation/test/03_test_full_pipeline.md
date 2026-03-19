## Run `generate_dirty_csv.md`'
`products_dirty.csv` is created.

Expected Output:
```
Reading reference data...
Generating DIRTY dataset for ETL testing...
Injecting guaranteed edge cases...
Done! Created DIRTY dataset with 13800 rows.
Saved to: data/raw/products_dirty.csv
```


## Run `transform.py`
Dirty data csv is transformed and cleaned.

`data/processed/products_clean.csv` & `data/processed/products_rejected.csv` are created.

Èxpected Output:
```
Starting ETL process...
ETL complete: 13800 input → 13388 valid → 412 rejected
ETL complete. Data saved to CSV. (Skipping database load)
```


## Run `generate_sales_csv.py`
Create the sales events

Expected Output:
```
Loading stores and clean product data...
Building virtual initial inventory (CROSS JOIN in Python)...
Simulating sales day by day for the last 730 days...
Created data/raw/orders.csv with 1446 historical receipts.
Created data/raw/items.csv with 2849 historical purchased items.
Created data/raw/inventories.csv with correct ending balance after 2 years of sales!
```

## Spin up Docker Container
Whole documentation in `02_test_newproduct.md`


## Data Validation Layer for STAGING in psql/pgadmin
### Staging Validation

/* Goal:
Confirm that events → Kafka → consumer → PostgreSQL (staging) 
is working AND that your data model reflects business logic correctly */

-- New Products Events
-- SELECT * FROM staging.products ORDER BY product_id DESC LIMIT 10;

-- Orders (Sales events)
-- SELECT * FROM staging.orders ORDER BY order_id DESC LIMIT 10;

-- Items (Check Fact Table is working)
-- SELECT * FROM staging.items ORDER BY order_id DESC LIMIT 10;

-- Inventory (KPI Table)
-- SELECT * FROM staging.inventories ORDER BY update_date DESC LIMIT 20;

-- Out of Stock Validation (Must be 0)
SELECT product_id, store_id, amount
FROM staging.inventories
WHERE amount < 0;

-- Order vs items consistency (Must be 0)
/*
SELECT o.order_id, o.order_price,
       SUM(i.item_price * i.quantity) AS calculated_total
FROM staging.orders o
JOIN staging.items i ON o.order_id = i.order_id
GROUP BY o.order_id, o.order_price
HAVING o.order_price != SUM(i.item_price * i.quantity);
*/

-- Product existence validation (Must be 0)
/*
SELECT i.product_id
FROM staging.items i
LEFT JOIN staging.products p ON i.product_id = p.product_id
WHERE p.product_id IS NULL;
*/

---

-- SELECT * FROM refined.items;
-- SELECT * FROM refined.products;
-- SELECT * FROM refined.orders;
-- SELECT refined.refresh_refined();
-- SELECT * FROM refined.inventories;
-- SELECT * FROM refined.stores;

-- REFRESH MATERIALIZED VIEW refined.items;
-- SELECT * FROM refined.items;


### Refined Validation
/*
Check that pipeline is fully working:
1. Kafka → staging
*/
-- SELECT COUNT(*) FROM staging.orders;
-- SELECT COUNT(*) FROM staging.items;


## 
/* Refined Updated Check*/
-- SELECT COUNT(*) FROM refined.items;

/* Business Validation

SELECT store_name, SUM(item_price * quantity) AS revenue
FROM refined.items
GROUP BY store_name;
*/


/*
Create the refined.orders technical view 
CREATE MATERIALIZED VIEW refined.orders AS
SELECT 
    o.order_id,
    o.order_date,
    s.store_name,
    s.city,
    o.order_price
FROM staging.orders o
JOIN staging.stores s ON s.store_id = o.store_id;
*/

-- Test the materialized refined.orders
-- SELECT * FROM refined.orders;


----

