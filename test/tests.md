# Tests
In terminal for one event sales

```
curl -X POST "http://localhost:8000/api/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 10001,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:30:00Z",
    "store_id": 1,
    "items": [
      {"product_id": 1, "price": 49.99, "quantity": 2},
      {"product_id": 2, "price": 29.50, "quantity": 1}
    ]
  }'
```

Or in Thunderclient: Single Events

- Create a new request
`Method: POST`

URL: http://localhost:8000/api/sales
(That endpoint exists in your FastAPI app.)

- Add header
Content-Type: application/json

- Paste this JSON in Body → JSON


```
{
    "event_id": 10001,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:30:00Z",
    "store_id": 1,
    "items": [
      {"product_id": 1, "price": 49.99, "quantity": 2},
      {"product_id": 2, "price": 29.50, "quantity": 1}
    ]
  }
```

```
{
  "event_id": 10002,
  "event_type": "sale",
  "timestamp": "2026-01-10T12:35:00Z",
  "store_id": 1,
  "items": [
    { "product_id": 1, "price": 49.99, "quantity": 1 },
    { "product_id": 2, "price": 29.50, "quantity": 2 }
  ]
}
```

```
{
  "event_id": 10003,
  "event_type": "sale",
  "timestamp": "2026-01-10T12:40:00Z",
  "store_id": 1,
  "items": [
    { "product_id": 1, "price": 59.99, "quantity": 1 }
  ]
}
```



URL: http://localhost:8000/api/sales/batch
```
[
  {
    "event_id": 10004,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:45:00Z",
    "store_id": 1,
    "items": [{ "product_id": 1, "price": 59.99, "quantity": 1 }]
  },
  {
    "event_id": 10005,
    "event_type": "sale",
    "timestamp": "2026-01-10T12:46:00Z",
    "store_id": 2,
    "items": [{ "product_id": 2, "price": 39.99, "quantity": 3 }]
  }
]
```

Confirm consumer processed it
`docker compose logs -f consumer`


Verify rows in Postgres/PgAdmin CLI
```
docker compose exec postgres psql -U postgres -d SportWearDB -c "SELECT COUNT(*) FROM staging.orders;"
docker compose exec postgres psql -U postgres -d SportWearDB -c "SELECT COUNT(*) FROM staging.items;"
docker compose exec postgres psql -U postgres -d SportWearDB -c "SELECT order_id, store_id, order_price, order_date FROM staging.orders ORDER BY order_id DESC LIMIT 5;"
docker compose exec postgres psql -U postgres -d SportWearDB -c "SELECT item_id, product_id, order_id, quantity, item_price FROM staging.items ORDER BY item_id DESC LIMIT 10;"
```


NOT DONE: Test User Story Queries
`docker compose exec postgres psql -U postgres -d SportWearDB -f /src_sql/user_story_queries.sql`

Should see “Caught sale event…” and DB save log lines. Check pgAdmin tables:

```
staging.orders

staging.items
```