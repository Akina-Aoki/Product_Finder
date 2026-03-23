# 🧪 Event Pipeline Testing Guide (FastAPI → Kafka → Postgres)
# 🧪 End-to-End Persistence Test Guide

## ⚡ Thunder Client Setup (IMPORTANT)
#### This guide starts **after** you have already done the following successfully: Everything in `03_test_full_pipeline.md`



POST: `http://localhost:8000/api/products/new`  
Content-Type: `application/json`  
1. Generated `data/raw/products_dirty.csv`.
2. Ran `scripts/transform.py` and created `data/processed/products_clean.csv`.
3. Ran `scripts/generate_sales_csv.py` and created:
   - `data/raw/orders.csv`
   - `data/raw/items.csv`
   - `data/raw/inventories.csv`
4. Started Docker with `docker compose up -d --build`.

👉 Use this format for ALL requests in Thunder Client:
- Method: **POST**
- Body type: **JSON**
- Header: `Content-Type: application/json`
At this point, the next step is to verify that:

- the historical seed data was loaded into **staging**,
- the materialized views in **refined** were created and refreshed,
- new API events are persisted correctly,
- Kafka is delivering messages to the consumer,
- PostgreSQL/pgAdmin shows the expected results.

---

## 🔄 0. Reset Environment
## 1. Reset and Start the Full Pipeline

Use this if you want a clean test from the beginning.

```bash
docker compose down -v
docker compose up -d --build
```

> `down -v` is important when you want PostgreSQL to rerun `sql/init.sql` and reload the CSV seed files from scratch.

---

## 🌐 1. Verify Services
## 2. Verify the Containers Are Healthy

```bash
docker compose ps
docker compose logs postgres --tail=50
docker compose logs consumer --tail=50
docker compose logs app --tail=50
```

- FastAPI: http://localhost:8000/docs  
- Kafka UI: http://localhost:8080  
### Expected

- `postgres`, `kafka`, `consumer`, and `app` should all be `Up`.
- PostgreSQL should finish initialization without CSV load errors.
- The consumer should print that it is listening to `inventory_events`.
- The API should be reachable on `http://localhost:8000/docs`.
- Kafka UI should be reachable on `http://localhost:8080`.

---

## 📡 Consumer Logs (MANDATORY CHECK)
## 3. Connect to PostgreSQL in psql

Always check Kafka logs when testing:
**If you want to verify everything from the terminal:**

```bash
docker compose logs -f consumer
docker exec -it SportWear_Postgres psql -U postgres -d SportWearDB
```

If your `.env` uses a different username, password, or database name, replace those values accordingly.

---

## Verify database seeded correctly
In pgadmin
```sql
SELECT * FROM staging.products;
SELECT * FROM staging.stores;
SELECT * FROM staging.inventories;
```
## 4. Connect in pgAdmin

Use pgAdmin to inspect the data visually.

## 📦 2. Schema Reference (API Contracts)
http://localhost:8000/api/sales
### 🧾 SaleEvent
```json
{
  "event_id": 10001,
  "event_type": "sale",
  "timestamp": "2026-01-10T12:30:00Z",
  "store_id": 1,
  "items": [
    {
      "product_id": 1,
      "price": 49.99,
      "quantity": 2
    }
  ]
}
```
### Connection settings

http://localhost:8000/api/sales/batch
```json
[
  {
    "event_id": 10001,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:30:00Z",
    "store_id": 1,
    "items": [
      {
        "product_id": 1,
        "price": 49.99,
        "quantity": 2
      }
    ]
  },
  {
    "event_id": 10002,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:35:00Z",
    "store_id": 2,
    "items": [
      {
        "product_id": 2,
        "price": 79.99,
        "quantity": 1
      },
      {
        "product_id": 3,
        "price": 19.99,
        "quantity": 3
      }
    ]
  }
]
```
- **Host**: `localhost`
- **Port**: `5439`
- **Database**: `SportWearDB`
- **Username**: `postgres`
- **Password**: `postgres`

If you changed the Docker environment variables, use the values from `docker-compose.yml` or your `.env` instead.

### In pgAdmin, expand:

- `Servers`
- your PostgreSQL server
- `Databases`
- `SportWearDB`
- `Schemas`
- `staging`
- `refined`

You should see the staging tables and refined materialized views created by `sql/init.sql`.

---

## 5. Validate That Seed Data Loaded into `staging`

Run these queries in **psql** or the **pgAdmin Query Tool**.

### 5.1 Check table row counts

Check the sale event in the database
```sql
SELECT * FROM staging.orders;
SELECT * FROM staging.items;
```

```sql
SELECT 'brands' AS table_name, COUNT(*) AS row_count FROM staging.brands
UNION ALL
SELECT 'categories', COUNT(*) FROM staging.categories
UNION ALL
SELECT 'colours', COUNT(*) FROM staging.colours
UNION ALL
SELECT 'genders', COUNT(*) FROM staging.genders
UNION ALL
SELECT 'sizes', COUNT(*) FROM staging.sizes
UNION ALL
SELECT 'stores', COUNT(*) FROM staging.stores
UNION ALL
SELECT 'products', COUNT(*) FROM staging.products
UNION ALL
SELECT 'inventories', COUNT(*) FROM staging.inventories
UNION ALL
SELECT 'orders', COUNT(*) FROM staging.orders
UNION ALL
SELECT 'items', COUNT(*) FROM staging.items
ORDER BY table_name;
```

### What this proves

- reference CSV data was copied into `staging`
- transformed products were loaded from `data/processed/products_clean.csv`
- the two years of generated sales history were loaded into `staging.orders` and `staging.items`
- ending inventory balances were loaded into `staging.inventories`

### 5.2 Spot-check the imported data

```sql
SELECT * FROM staging.products ORDER BY product_id LIMIT 10;
SELECT * FROM staging.stores ORDER BY store_id;
SELECT * FROM staging.orders ORDER BY order_id DESC LIMIT 10;
SELECT * FROM staging.items ORDER BY item_id DESC LIMIT 10;
SELECT * FROM staging.inventories ORDER BY inventory_id DESC LIMIT 10;
```

---

### 👉 NewProductEvent
http://localhost:8000/api/products/new
```json
{
  "event_id": 1,
  "event_type": "new_product",
  "timestamp": "2026-01-15T10:00:00Z",
  "product": {
    "product_code": 999001,
    "product_name": "Test Jacket",
    "brand_id": 1,
    "category_id": 2,
    "colour_id": 1,
    "size_id": 3,
    "gender_id": 1,
    "price": 99.99
  }
}
```
## 6.  👉 Validate That `refined` Exists and Contains Data

http://localhost:8000/api/products/new/batch
```json
[
  {
    "event_id": 1,
    "event_type": "new_product",
    "timestamp": "2026-01-15T10:00:00Z",
    "product": {
      "product_code": 999001,
      "product_name": "Test Jacket",
      "brand_id": 1,
      "category_id": 2,
      "colour_id": 1,
      "size_id": 3,
      "gender_id": 1,
      "price": 99.99
    }
  },
  {
    "event_id": 2,
    "event_type": "new_product",
    "timestamp": "2026-01-15T10:05:00Z",
    "product": {
      "product_code": 999002,
      "product_name": "Test Hoodie",
      "brand_id": 1,
      "category_id": 3,
      "colour_id": 2,
      "size_id": 4,
      "gender_id": 1,
      "price": 79.99
    }
  }
]
```
The refined layer is built as **materialized views** from staging.

Test new products
### 6.1 Check row counts in refined

```sql
SELECT 'products' AS view_name, COUNT(*) AS row_count FROM refined.products
UNION ALL
SELECT 'stores', COUNT(*) FROM refined.stores
UNION ALL
SELECT 'inventories', COUNT(*) FROM refined.inventories
UNION ALL
SELECT 'items', COUNT(*) FROM refined.items
UNION ALL
SELECT 'orders', COUNT(*) FROM refined.orders
ORDER BY view_name;
```

```sql
SELECT *
FROM staging.products
ORDER BY product_id DESC
LIMIT 10;
```

### 6.2 Compare staging vs refined counts

```sql
SELECT 'products' AS entity,
        (SELECT COUNT(*) FROM staging.products) AS staging_count,
        (SELECT COUNT(*) FROM refined.products) AS refined_count
UNION ALL
SELECT 'stores',
        (SELECT COUNT(*) FROM staging.stores),
        (SELECT COUNT(*) FROM refined.stores)
UNION ALL
SELECT 'inventories',
        (SELECT COUNT(*) FROM staging.inventories),
        (SELECT COUNT(*) FROM refined.inventories)
UNION ALL
SELECT 'items',
        (SELECT COUNT(*) FROM staging.items),
        (SELECT COUNT(*) FROM refined.items)
UNION ALL
SELECT 'orders',
        (SELECT COUNT(*) FROM staging.orders),
        (SELECT COUNT (*) FROM refined.orders);
```

Validate Specific Batch
### Important note about `refined`

The refined layer does **not** auto-update instantly after each API event.

It is refreshed by:

- `SELECT refined.refresh_refined();` manually, or
- the scheduled `pg_cron` job every **15 minutes**.

So after you insert a new sale, restock, or product event, you should refresh manually before validating `refined`.

### 6.3 Refresh refined manually

```sql
SELECT refined.refresh_refined();
```
SELECT *
FROM staging.products
WHERE product_code IN (999001, 999002);

### 6.4 Inspect refined data

```sql
SELECT * FROM refined.products ORDER BY product_id DESC LIMIT 10;
SELECT * FROM refined.inventories ORDER BY inventory_id DESC LIMIT 10;
SELECT * FROM refined.items ORDER BY item_id DESC LIMIT 10;
```

---

### 👉 InventoryEvent (IMPORTANT)
**We do NOT have and not need an endpoint for SINGLE inventory events.**

### Add new product first in the products
POST: http://localhost:8000/api/products/new
**DOUBLE CHECK THE PRODUCT_ID**

```json
{
  "event_id": 10001,
  "event_type": "new_product",
  "timestamp": "2026-03-18T08:00:00Z",
  "product": {
    "product_code": 11111111,
    "product_name": "Test Shirt",
    "brand_id": 1,
    "category_id": 1,
    "colour_id": 1,
    "size_id": 1,
    "gender_id": 1,
    "price": 29.99
  }
}
```
Check in staging
```sql
-- SELECT * FROM staging.products;
SELECT * FROM staging.products WHERE product_id = 14401;
```


## 7.👉  Validate That the Refresh Job Exists

http://localhost:8000/api/inventory-events/batch
```
[
  {
    "event_id": 20001,
    "event_type": "restock",
    "timestamp": "2026-03-18T08:44:02.011Z",
    "store_id": 1,
    "product_id": 14401,
    "quantity_change": 10,
    "stock_after_event": 50
  },
  {
    "event_id": 20002,
    "event_type": "restock",
    "timestamp": "2026-03-18T08:50:00.000Z",
    "store_id": 2,
    "product_id": 14401,
    "quantity_change": 5,
    "stock_after_event": 30
  }
]
```
This confirms that `pg_cron` scheduled the periodic refresh job.

Validate the inventory events
```sql
SELECT *
FROM staging.inventories
WHERE product_id = 14401
ORDER BY update_date DESC;
```

```sql
SELECT jobid, schedule, command, active
FROM cron.job
ORDER BY jobid;
```

### Expected

You should see a job similar to:

- schedule: `*/15 * * * *`
- command: `SELECT refined.refresh_refined();`

---

## 🧪 3. Test: New Product
## 8. Test New API Events End-to-End

**POST**
```
/api/products/new
After validating the seeded data, the next step is to verify that **new** events flow through:

**API → Kafka → consumer → staging → refined**

Always keep the consumer logs open while testing:

```bash
docker compose logs -f consumer
```

---

## 9. 👉 Test a New Product Event

### Endpoint

`POST http://localhost:8000/api/products/new`

### JSON body

```json
{
  "event_id": 1,
  "event_id": 910001,
  "event_type": "new_product",
  "timestamp": "2026-01-15T10:00:00Z",
  "timestamp": "2026-03-19T10:00:00Z",
  "product": {
    "product_code": 999001,
    "product_name": "Test Jacket",
    "brand_id": 1,
    "category_id": 2,
    "colour_id": 1,
    "size_id": 3,
    "gender_id": 1,
    "price": 99.99
  }
}
```

### ✅ Validate in Postgres
### Validate in `staging`

```sql
SELECT * FROM staging.products ORDER BY product_id DESC;
SELECT *
FROM staging.products
WHERE product_code = 999001;

SELECT *
FROM staging.inventories
WHERE product_id = (
  SELECT product_id FROM staging.products WHERE product_code = 999001
)
ORDER BY store_id;
```

---
### Expected

## 🧪 4. Test: Sales
- one new row in `staging.products`
- inventory rows created for stores `1` and `2`
- each new inventory row has `amount = 10`

**POST**
```
/api/sales
### Validate in `refined`

```sql
SELECT refined.refresh_refined();

SELECT *
FROM refined.products
WHERE product_id = (
  SELECT product_id FROM staging.products WHERE product_code = 999001
);
```

---

## 10. 👉 Test a Sale Event

### Endpoint

`POST http://localhost:8000/api/sales`

### JSON body

```json
{
  "event_id": 920001,
  "event_type": "sale",
  "timestamp": "2026-03-19T10:15:00Z",
  "store_id": 1,
  "items": [
    {
      "product_id": 14401,
      "price": 49.99,
      "quantity": 2
    }
  ]
}
```

### ✅ Validate
### Validate in `staging`

```sql
SELECT * FROM staging.orders WHERE order_id = 1476 ORDER BY order_id;
SELECT * FROM staging.items WHERE order_id = 1476 ORDER BY item_id;
```

Check in the orders and items tables
```sql
SELECT *
FROM staging.orders
WHERE source_event_id = '920001';

SELECT i.*
FROM staging.items i
JOIN staging.orders o ON o.order_id = i.order_id
WHERE o.source_event_id = '920001';
```

```sql
SELECT *
FROM staging.inventories
WHERE product_id = 1 AND store_id = 1;
```

---
### Expected

## 🧪 👉 Test: Inventory (Restock)
- a new row is inserted into `staging.orders`
- one or more rows are inserted into `staging.items`
- inventory for the sold product decreases in `staging.inventories`

**POST**
```
/api/inventory-events/batch
### Validate in `refined`

```sql
SELECT refined.refresh_refined();

SELECT *
FROM refined.items
WHERE order_id = (
  SELECT order_id FROM staging.orders WHERE source_event_id = '920001'
);
```

---

## 11. 👉 Test a Restock Event

### Endpoint

`POST http://localhost:8000/api/inventory-events/batch`

### JSON body

```json
[
  {
    "event_id": 930001,
    "event_type": "restock",
    "timestamp": "2026-03-19T10:30:00Z",
    "store_id": 1,
    "product_id": 14401,
    "quantity_change": 10,
    "stock_after_event": 50
  }
]
```

### ✅ Validate
### Validate in `staging`

```sql
SELECT *
FROM staging.inventories
WHERE product_id = 14401
ORDER BY update_date DESC;
```

### Expected

- inventory amount increases for the matching `(store_id, product_id)` row
- `update_date` changes to the event timestamp

### Validate in `refined`

```sql
SELECT refined.refresh_refined();
```


```sql
SELECT *
FROM refined.inventories
WHERE product_id = 14401
  AND store_name = (
    SELECT store_name 
    FROM staging.stores 
    WHERE store_id = 1
  );
```

---


## 13. Validate Kafka Delivery

Open Kafka UI:

- `http://localhost:8080`

Check:
- Topic: `inventory_events`
- Messages are arriving
- JSON is correctly structured

---
- topic `inventory_events` exists
- messages are arriving after API calls
- payloads are valid JSON

## More Checks
You can also verify from logs:

### Ensure no negative inventory 
```bash
docker compose logs -f consumer
docker compose logs -f app
```


### Ensure referential integrity (products exist) 
## 14. Data Integrity Checks for PostgreSQL / pgAdmin

These are the most important SQL checks to include in your test documentation.

### 14.1 No negative inventory

```sql
SELECT *
FROM staging.inventories
WHERE amount < 0;
```

**Expected:** `0 rows`

### 14.2 Every inventory row references a real product

```sql
SELECT i.*
FROM staging.inventories i
LEFT JOIN staging.products p ON p.product_id = i.product_id
WHERE p.product_id IS NULL;
```
sql SELECT i.* FROM staging.inventories i LEFT JOIN staging.products p ON i.product_id = p.product_id WHERE p.product_id IS NULL; 
``` 

✔ Expect: **0 rows**
---


### Ensure orders link to items correctly
 ```
sql SELECT o.order_id, i.item_id FROM staging.orders o LEFT JOIN staging.items i ON o.order_id = i.order_id WHERE i.item_id IS NULL; 
``` 
### 14.3 Every item references a real order

✔ Expect: **0 rows**
```sql
SELECT i.*
FROM staging.items i
LEFT JOIN staging.orders o ON o.order_id = i.order_id
WHERE o.order_id IS NULL;
```

----

### Ensure referential integrity (products exist)
### 14.4 Every order has at least one item

```sql
SELECT o.order_id, o.source_event_id
FROM staging.orders o
LEFT JOIN staging.items i ON i.order_id = o.order_id
GROUP BY o.order_id, o.source_event_id
HAVING COUNT(i.item_id) = 0;
```
SELECT i.* FROM staging.inventories i LEFT JOIN staging.products p ON i.product_id = p.product_id;

**Expected:** `0 rows`

### 14.5 Compare a staged order with its refined representation

```sql
SELECT o.order_id, o.source_event_id, o.store_id, o.order_price, o.order_date
FROM staging.orders o
WHERE o.source_event_id = '920001';

SELECT *
FROM refined.items
WHERE order_id = (
  SELECT order_id FROM staging.orders WHERE source_event_id = '920001'
);
```

**Expected:**

- the order exists in `staging.orders`
- related rows exist in `staging.items`
- related rows appear in `refined.items` after refresh

### 14.6 Compare staging vs refined after a manual refresh

```sql
SELECT refined.refresh_refined();

SELECT
  (SELECT COUNT(*) FROM staging.products)    AS staging_products,
  (SELECT COUNT(*) FROM refined.products)    AS refined_products,
  (SELECT COUNT(*) FROM staging.stores)      AS staging_stores,
  (SELECT COUNT(*) FROM refined.stores)      AS refined_stores,
  (SELECT COUNT(*) FROM staging.inventories) AS staging_inventories,
  (SELECT COUNT(*) FROM refined.inventories) AS refined_inventories,
  (SELECT COUNT(*) FROM staging.items)       AS staging_items,
  (SELECT COUNT(*) FROM refined.items)       AS refined_items;
```
✔ Expect: products listed

**Expected:** counts should align for the entities that are materialized from staging.

---