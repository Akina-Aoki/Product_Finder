## Step A: Infrastructure boots
`docker-compose.yml` starts:

- `postgres` (DB)
- `kafka` (broker)
- `kafka-ui` (visual monitoring)
- `consumer` (DB writer)
- `app` (FastAPI endpoint)

---

## Step B — DB gets initialized with schema + seed data

On first `Postgres` startup, `sql/init.sql` is auto-executed and:

- creates schema `staging`
- creates dimension/reference tables + fact-like tables
- loads CSVs from `data/raw`
- resets serial sequences to max IDs after `COPY` load

---

## Step C — API receives sale events

FastAPI exposes:

- `POST /api/sales` for one sale event
- `POST /api/sales/batch` for many events

The payload is validated with `Pydantic` (`SaleEvent` / `SaleItem`).

---

## Step D — API publishes to Kafka

When request is valid, API uses `KafkaProducer.send()` to push event JSON into topic `inventory_events` (configurable by env var).

Then `flush()` ensures send completion before returning success message.

---

## Step E — Consumer reads Kafka and writes DB

Consumer polls Kafka in a `while True` loop.

For each message:

- decode JSON (with a fallback parse because payload may be double-encoded string)
- if `event_type == "sale"`, compute order total from item lines
- insert one row into `staging.orders`
- insert many rows into `staging.items` (1 per sold item)

---

So architecturally:

`API` = ingestion endpoint  
`Kafka` = durable event bus  
`consumer` = sink connector / business loader  
`Postgres` = analytical store / staging mart