# Sprint 3 
We have finished the following and connected the 2 pipelines (ETL + Kafka Event Streaming):

### 1. Batch ETL for product master data
The project includes a cleaning pipeline for product records:

- `scripts/generate_dirty_csv.py` creates intentionally messy product data for validation testing.
- `scripts/transform.py` validates, cleans, rejects bad rows, and produces curated CSV outputs.
- `scripts/load_products.py` can load the cleaned products into PostgreSQL.

This establishes the **batch ETL foundation** of the platform. Dirty input is separated from clean, analytics-ready product data. 

### 2. Event-driven ingestion via Kafka
The project also includes a streaming workflow:

- `app/main.py` exposes FastAPI endpoints for inventory-related events.
- The API publishes events to the Kafka topic `inventory_events`.
- `app/consumer/db_consumer.py` consumes those events and writes the results to PostgreSQL.

This establishes the **real-time / near-real-time ingestion layer** of the platform.

### 3. PostgreSQL as analytical storage
`sql/init.sql` creates two database layers:

- `staging`: operational/raw-ish relational storage,
- `refined`: materialized views intended for analytics consumption.

The refined layer is refreshed by the `refined.refresh_refined()` function and scheduled with `pg_cron` every 15 minutes.


### Sprint 4
This is the start of the **serving layer** that can later power BI tools, customer dashboards.

Query layer for analytics and dashboards
`sql/user_story_queries.sql` contains business-oriented SQL for:

- product movement,
- stock visibility,
- revenue analysis,
- best/lowest performing products,
- and other dashboard-friendly metrics.



