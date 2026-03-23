````md
# 🧪 Event Pipeline Testing Guide (FastAPI → Kafka → Postgres)

## ⚡ Thunder Client Setup (IMPORTANT)

POST: `http://localhost:8000/api/products/new`  
Content-Type: `application/json`  

👉 Use this format for ALL requests in Thunder Client:
- Method: **POST**
- Body type: **JSON**
- Header: `Content-Type: application/json`

---

## 🔄 0. Reset Environment

```bash
docker compose down -v
docker compose up -d --build
```

---

## 🌐 1. Verify Services

- FastAPI: http://localhost:8000/docs  
- Kafka UI: http://localhost:8080  

---

## 📡 Consumer Logs (MANDATORY CHECK)

Always check Kafka logs when testing:

```bash
docker compose logs -f consumer
```

---

## Verify database seeded correctly in staging
In pgadmin
```sql
SELECT * FROM staging.products;
SELECT * FROM staging.stores;
SELECT * FROM staging.inventories;
```


## 👉 2. Schema Reference (API Contracts)
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

Check the sale event in the database
```sql
SELECT * FROM staging.orders;
SELECT * FROM staging.items;

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

👉 http://localhost:8000/api/products/new/batch
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

Test new products
```
SELECT *
FROM staging.products
ORDER BY product_id DESC
LIMIT 10;
```

Validate Specific Batch
```
SELECT *
FROM staging.products
WHERE product_code IN (999001, 999002);
```
---

### 👉 InventoryEvent (IMPORTANT)

http://localhost:8000/api/inventory-events/batch
```
[
  {
    "event_id": 20001,
    "event_type": "restock",
    "timestamp": "2026-03-18T08:44:02.011Z",
    "store_id": 1,
    "product_id": 1,
    "quantity_change": 10,
    "stock_after_event": 50
  },
  {
    "event_id": 20002,
    "event_type": "restock",
    "timestamp": "2026-03-18T08:50:00.000Z",
    "store_id": 1,
    "product_id": 2,
    "quantity_change": 5,
    "stock_after_event": 30
  },
  {
    "event_id": 20003,
    "event_type": "restock",
    "timestamp": "2026-03-18T09:00:00.000Z",
    "store_id": 2,
    "product_id": 1,
    "quantity_change": 20,
    "stock_after_event": 70
  }
]
```

Validate the inventory events
```
SELECT *
FROM staging.inventories
WHERE product_id IN (1, 2)
ORDER BY update_date DESC;
```

---

## 👉 3. Test: New Product

**POST**
```
/api/products/new
```

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

### ✅ Validate in Postgres
```sql
SELECT * FROM staging.products ORDER BY product_id DESC;
```

---

## 🧪 4. Test: Sales

**POST**
```
/api/sales
```

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

### ✅ Validate
```sql
SELECT * FROM staging.orders ORDER BY order_id DESC;
SELECT * FROM staging.items ORDER BY item_id DESC;
```

---

## 🧪 5. Test: Inventory (Restock)

**POST**
```
/api/inventory-events/batch
```

```json
[
  {
    "event_id": 20001,
    "event_type": "restock",
    "timestamp": "2026-03-18T08:44:02.011Z",
    "store_id": 1,
    "product_id": 1,
    "quantity_change": 10,
    "stock_after_event": 50
  }
]
```

### ✅ Validate
```sql
SELECT * FROM staging.inventories
WHERE product_id = 1 AND store_id = 1;
```

---

## 🧪 6. Test: Inventory (Stock Update)
http://localhost:8000/api/inventory-events/batch
```json
[
  {
    "event_id": 20002,
    "event_type": "stock_update",
    "timestamp": "2026-03-18T08:45:00.000Z",
    "store_id": 1,
    "product_id": 1,
    "quantity_change": 0,
    "stock_after_event": 30
  }
]
```

### ✅ Validate
```sql
SELECT * FROM staging.inventories
WHERE product_id = 1 AND store_id = 1;
```

---

## 🔍 7. Kafka Validation

Open:
```
http://localhost:8080
```

Check:
- Topic: `inventory_events`
- Messages are arriving
- JSON is correctly structured

---

## More Checks

### Ensure no negative inventory 
```
sql SELECT * FROM staging.inventories WHERE amount < 0; ``` 
✔ Expect: **0 rows**


---

### Ensure referential integrity (products exist) 
```
sql SELECT i.* FROM staging.inventories i LEFT JOIN staging.products p ON i.product_id = p.product_id WHERE p.product_id IS NULL; 
``` 

✔ Expect: **0 rows**
---

### Ensure orders link to items correctly
 ```
sql SELECT o.order_id, i.item_id FROM staging.orders o LEFT JOIN staging.items i ON o.order_id = i.order_id WHERE i.item_id IS NULL; 
``` 

✔ Expect: **0 rows**

----

### Ensure referential integrity (products exist)

```
SELECT i.* FROM staging.inventories i LEFT JOIN staging.products p ON i.product_id = p.product_id;
```
✔ Expect: products listed
---



