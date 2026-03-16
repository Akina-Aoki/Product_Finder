# Integration validation of `new_product` endpoint

FastAPI → Kafka → Consumer → PostgreSQL

## Rebuild Platform (Docker)
```
docker compose down -v
docker compose up -d --build
docker ps
```

Kafka UI
`http://localhost:8080`

FastAPI
`http://localhost:8000/docs`

Always check Kafka logs when testing:
`docker compose logs -f consumer` in terminal.


PSQL PGAdmin
```
SELECT * FROM staging.products;
SELECT * FROM staging.inventories;
```

## Test Order for pipeline validation
This proves inventory movement tracking works.
1️⃣ Create new product OK
2️⃣ Verify product table OK
3️⃣ Verify inventory seeded OK
4️⃣ Run sale event (single + batch) OK
5️⃣ Verify inventory decreases OK
6️⃣ Run restock event
7️⃣ Verify inventory increases
8️⃣ Run stock update
9️⃣ Verify absolute inventory change


## Test `new_product` SINGLE EVENT
POST: `http://localhost:8000/api/products/new`
Content Type: application/json

payload:
```
{
  "event_id": 30001,
  "event_type": "new_product",
  "timestamp": "2026-01-15T10:00:00Z",
  "product": {
    "product_code": 2119431,
    "product_name": "Black T-Shirt",
    "brand_id": 1,
    "category_id": 2,
    "colour_id": 1,
    "size_id": 3,
    "gender_id": 1,
    "price": 29.99
  }
}
```

### Find created product_id in products table
```
SELECT product_id, product_code, product_name
FROM staging.products
WHERE product_code = 2119431;
```

### Find created product_id in inventories table

```
SELECT *
FROM staging.inventories
WHERE product_id = (
  SELECT product_id
  FROM staging.products
  WHERE product_code = 2119431
);
```

## Test `new_product` EVENT BATCH
SEND: POST `http://localhost:8000/api/products/new/batch`
```
[
  {
    "event_id": 30002,
    "event_type": "new_product",
    "timestamp": "2026-01-15T10:00:00Z",
    "product": {
      "product_code": 2219431,
      "product_name": "Black T-Shirt",
      "brand_id": 1,
      "category_id": 2,
      "colour_id": 1,
      "size_id": 3,
      "gender_id": 1,
      "price": 29.99
    }
  },
  {
    "event_id": 30003,
    "event_type": "new_product",
    "timestamp": "2026-01-15T10:05:00Z",
    "product": {
      "product_code": 2319432,
      "product_name": "Blue Hoodie",
      "brand_id": 1,
      "category_id": 3,
      "colour_id": 2,
      "size_id": 4,
      "gender_id": 1,
      "price": 59.99
    }
  }
]
```

Validate in psql
```
SELECT product_id, product_code, product_name
FROM staging.products
WHERE product_code IN (2219431, 2319432)
ORDER BY product_code;
```

OR check by LATEST inserts
```
SELECT *
FROM staging.products
ORDER BY product_id DESC
LIMIT 5;
```

-----

## Test Sale (single)
Endpoint:
`POST /api/sales`

Body:
```
{
  "event_id": 40001,
  "event_type": "sale",
  "timestamp": "2026-01-15T12:00:00Z",
  "store_id": 1,
  "items": [
    {
      "product_id": 21,
      "price": 29.99,
      "quantity": 2
    }
  ]
}
```

In PGAdmin:
```
SELECT *
FROM staging.inventories
WHERE product_id = 21 AND store_id = 1;
```
Amount should be = 8

## Test Sale (batch)

Endpoint:
`http://localhost:8000/api/sales/batch`

Body:
```
[
  {
    "event_id": 40002,
    "event_type": "sale",
    "timestamp": "2026-01-15T12:05:00Z",
    "store_id": 1,
    "items": [
      {
        "product_id": 21,
        "price": 29.99,
        "quantity": 1
      }
    ]
  },
  {
    "event_id": 40003,
    "event_type": "sale",
    "timestamp": "2026-01-15T12:06:00Z",
    "store_id": 1,
    "items": [
      {
        "product_id": 22,
        "price": 59.99,
        "quantity": 2
      }
    ]
  }
]
```

Check in DB:
```
SELECT * FROM staging.orders ORDER BY order_id DESC;

SELECT * FROM staging.items ORDER BY item_id DESC;
```

---

## Test Restock (single)
Endpoint: POST `http://localhost:8000/api/inventory-events`

Body:
```
{
  "event_id": 50001,
  "event_type": "restock",
  "timestamp": "2026-01-15T13:00:00Z",
  "store_id": 1,
  "product_id": 21,
  "quantity_change": 5
}
```
Check DB:
```
SELECT *
FROM staging.inventories
WHERE product_id = 21 AND store_id = 1;
```
Expect to be: inventory = previous + 5

## Test Restock (batch)

Endpoint: POST `http://localhost:8000/api/inventory-events/batch`

Body:
```
[
  {
    "event_id": 50002,
    "event_type": "restock",
    "timestamp": "2026-01-15T13:05:00Z",
    "store_id": 1,
    "product_id": 21,
    "quantity_change": 3
  },
  {
    "event_id": 50003,
    "event_type": "restock",
    "timestamp": "2026-01-15T13:06:00Z",
    "store_id": 1,
    "product_id": 22,
    "quantity_change": 4
  }
]
```
CHeck inventory DB:
```
SELECT *
FROM staging.inventories
WHERE product_id IN (21,22)
ORDER BY product_id, store_id;
```

----

## Test Stock Update (single)

Endpoint: POST: `http://localhost:8000/api/inventory-events`

BODY:
```
{
  "event_id": 60001,
  "event_type": "stock_update",
  "timestamp": "2026-01-15T14:00:00Z",
  "store_id": 1,
  "product_id": 21,
  "quantity_change": 0,
  "stock_after_event": 20
}
```
inventory = 20

## Test Stock Update (batch)

Endpoint: POST: `http://localhost:8000/api/inventory-events/batch`

BODY:
```
[
  {
    "event_id": 60002,
    "event_type": "stock_update",
    "timestamp": "2026-01-15T14:05:00Z",
    "store_id": 1,
    "product_id": 21,
    "quantity_change": 0,
    "stock_after_event": 15
  },
  {
    "event_id": 60003,
    "event_type": "stock_update",
    "timestamp": "2026-01-15T14:06:00Z",
    "store_id": 1,
    "product_id": 22,
    "quantity_change": -2
  }
]
```