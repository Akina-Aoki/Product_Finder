# Tests Core Event Pipeline
1. Sales pipeline
2. Sales batch
3. Inventory restock
4. Inventory batch
5. Stock update

## Consumer Logic
```
if event_type == "sale":
    process_sale_event()

elif event_type == "restock":
    process_restock_event()

elif event_type == "stock_update":
    process_stock_update_event()
```

## Test /api/sales (Single Event)
- Client → FastAPI → Kafka → Consumer → Postgres
- UI for Apache Kafka
`http://localhost:8080/`

SEND: POST
```
http://localhost:8000/api/sales
```


```
{
  "event_id": 10001,
  "event_type": "sale",
  "timestamp": "2026-01-10T12:30:00Z",
  "store_id": 1,
  "items": [
    {"product_id": 1, "price": 49.99, "quantity": 2}
  ]
}
```

Test in DB:
```
SELECT * FROM staging.orders ORDER BY order_id;
SELECT * FROM staging.items ORDER BY item_id;

SELECT * FROM staging.inventories
WHERE product_id = 1 AND store_id = 1;
```

## Test /api/sales/batch

SEND: POST
```
http://localhost:8000/api/sales/batch
```

```
[
  {
    "event_id": 10002,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:35:00Z",
    "store_id": 1,
    "items": [
      {"product_id": 1, "price": 49.99, "quantity": 1}
    ]
  },
  {
    "event_id": 10003,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:36:00Z",
    "store_id": 2,
    "items": [
      {"product_id": 2, "price": 29.50, "quantity": 3}
    ]
  }
]
```

Test in DB: Order should increase
`SELECT COUNT(*) FROM staging.orders;`


## Test /api/inventory-events (Restock)
SEND: POST
`http://localhost:8000/api/inventory-events`

```
{
  "event_id": 30001,
  "event_type": "restock",
  "timestamp": "2026-01-11T10:05:00Z",
  "store_id": 1,
  "product_id": 1,
  "quantity_change": 10
}
```

Verify Inventory increased:
`SELECT product_id, store_id, amount FROM staging.inventories WHERE product_id=1 AND store_id=1;`

## Test /api/inventory-events/batch
SEND: POST
`http://localhost:8000/api/inventory-events/batch`


```
[
  {
    "event_id": 30002,
    "event_type": "restock",
    "timestamp": "2026-01-11T10:10:00Z",
    "store_id": 1,
    "product_id": 2,
    "quantity_change": 5
  },
  {
    "event_id": 30003,
    "event_type": "restock",
    "timestamp": "2026-01-11T10:12:00Z",
    "store_id": 2,
    "product_id": 1,
    "quantity_change": 8
  }
]
```

Verify: 
```
SELECT product_id, store_id, amount FROM staging.inventories;
```

## Test stock_update
SEND: POST
`http://localhost:8000/api/inventory-events`

```
[
  {
    "event_id": 30004,
    "event_type": "stock_update",
    "timestamp": "2026-01-11T10:20:00Z",
    "store_id": 1,
    "product_id": 1,
    "quantity_change": 0,
    "stock_after_event": 50
  }
]
```

Verify consumer hanled it: `docker compose logs -f consumer`
Expect: 
```
SportWear_Consumer  | Caught stock_update event from Kafka! (Event ID: 30004)
SportWear_Consumer  | Stock update event saved (Event ID: 30004)
```

Verify in DB: 
```
SELECT product_id, store_id, amount FROM staging.inventories WHERE product_id=1 AND store_id=1;
```
amount must be = 50

------

# More integrity testing
## Orders vs Items relationship
- Each order has matching items
- order_price equals sum(price * quantity)

```
SELECT o.order_id,
       COUNT(i.item_id) AS item_count,
       o.order_price
FROM staging.orders o
LEFT JOIN staging.items i
ON o.order_id = i.order_id
GROUP BY o.order_id, o.order_price
ORDER BY o.order_id DESC;
```

## Inventory NEVER negative
```
SELECT *
FROM staging.inventories
WHERE amount < 0;
```

## Check stock after event
- sales decreased stock
- restock increased stock
- stock_update set absolute value

```
SELECT product_id, store_id, amount
FROM staging.inventories
ORDER BY product_id, store_id;
```

## Event Idempotency
````
SELECT COUNT(*)
FROM staging.orders
WHERE source_event_id = '10001';
```
Should give 1