# Sprint #2 Backlog Plan (4 Days)

## Why this sprint order
To maximize value in 4 days, we should build a **thin vertical slice** end-to-end:
1) infrastructure up, 2) valid event data, 3) database model, 4) ingestion + useful SQL outputs.

This directly supports our MVP goals: track inventory movement, detect restocking in inventory, monitor sales, and analyze revenue from streamed events.

---

## Sprint Goal
By end of Sprint #2, the team can:
- Run Kafka + PostgreSQL in Docker Compose
- Produce simulated inventory events from JSONL
- Validate and load events into PostgreSQL tables
- Run SQL queries that answer MVP business questions

---

## Priority (must-have first)

### P0 (Must finish this sprint #2)
- Docker Compose with Kafka and PostgreSQL running reliably
- Event schema contract finalized and documented
- JSONL dataset generator/seed file aligned with schema
- Consumer/loader writes validated events into PostgreSQL
- 4-6 core SQL queries for MVP questions

### P1 (Should finish if time remains)
- Basic data quality checks (nulls, invalid event_type, negative stock_after_event)
- Indexes for query performance on timestamp/product_id/event_type
- Lightweight README runbook for local setup and demo steps

### Aim in Sprint #3
- Dashboard/API layer
- Advanced analytics and forecasting (CTIs, etc. **still undecided**)


---

## Backlog Breakdown 

## Part 1: Spinning up Docker container for Kafka (plus PostgreSQL)

### User Story
As a developer, I want Kafka + PostgreSQL in Docker so we can run the pipeline consistently on all machines.

### Tasks (small, actionable)
1. Define `docker-compose.yml` services
   - `zookeeper` (if using classic Kafka image)
   - `kafka`
   - `postgres`
   - optional `kafka-ui` for visibility
2. Add environment variables and ports
   - Kafka broker listener config
   - Postgres user/password/db name
3. Add healthchecks and startup dependencies
   - Postgres healthcheck
   - Kafka readiness check
4. Create persistent volumes
   - postgres data volume
   - kafka data volume (if needed)
5. Add one command to start everything
   - `docker compose up -d`
6. Verify services are reachable from host and containers
   - Kafka topic list works
   - Postgres connection works

### Acceptance Criteria
- `docker compose up -d` starts all required services with no crash loop.
- Team can connect to Postgres and Kafka from local Python scripts.
- README contains exact start/stop commands.

### Definition of Done
- Compose file committed
- `.env.example` documented (no real secrets)
- Verification commands/screenshots/log snippets attached in PR

---

## Part 2: JSONL file that simulates real-time data

### User Story
As a data engineer, I want realistic inventory events in JSONL so we can test the stream and database loading.

### Event Schema (recommended)
Required:
- `event_id` (unique)
- `timestamp` (ISO-8601 UTC)
- `event_type` (`purchase`, `restock`, `inventory_update`)
- `product_id`
- `product_name`
- `category`
- `price`
- `quantity_change` (negative for purchase, positive for restock)
- `stock_after_event`
- `warehouse_id`

### Tasks
1. Finalize schema contract and event rules
   - purchase => `quantity_change < 0`
   - restock => `quantity_change > 0`
2. Create sample JSONL dataset file
   - at least 300-1000 events for useful queries
   - multiple products and categories
3. Add a simulator script
   - emits lines to Kafka topic at configurable interval
4. Add validation logic (Pydantic)
   - reject bad events, log reason
5. Add data quality report
   - counts by event_type
   - invalid row count

### Acceptance Criteria
- Every JSONL line parses as valid JSON and schema-valid event.
- Event distribution includes purchase/restock/inventory_update.
- Simulator can run for N events and publish to Kafka.

### Definition of Done
- Schema markdown + JSONL sample committed
- Validation script passes on clean data
- Invalid sample file included for negative testing (optional)

---

## Part 3: Create data modeling of the database as far as needed

### User Story
As an analyst/manager, I want a clean data model so I can answer sales, restock, and revenue questions correctly.

### Recommended MVP Data Model (simple and strong)
1. `dim_products`
   - product_id (PK), product_name, category
2. `dim_warehouses`
   - warehouse_id (PK), warehouse_name (optional)
3. `fact_inventory_events`
   - event_id (PK), event_ts, event_type,
   - product_id (FK), warehouse_id (FK),
   - price, quantity_change, stock_after_event

Optional snapshot table (if needed):
4. `fact_inventory_snapshot`
   - product_id, warehouse_id, current_stock, updated_at

### Tasks
1. Draw ERD (can be Mermaid/dbdiagram)
2. Write SQL DDL for the 3 core tables
3. Add constraints
   - event_type check
   - non-null constraints
   - PK/FK constraints
4. Add indexes
   - `(event_ts)`, `(product_id, event_ts)`, `(event_type)`
5. Document grain of fact table
   - one row = one inventory event

### Acceptance Criteria
- ERD and DDL are aligned with JSONL schema.
- Loading script inserts without schema mismatch.
- Core SQL questions can be answered from model.

### Definition of Done
- ERD file committed
- SQL schema migration/init script committed
- Constraints verified with insert tests

---

## Part 4: Processing data and loading into PostgreSQL + SQL queries

### User Story
As a product owner, I want data loaded and queryable so stakeholders can see business value this sprint.

### Tasks
1. Build ingestion flow
   - consume event from Kafka
   - validate event
   - transform field names/types
   - upsert dimensions
   - insert fact event
2. Add idempotency protection
   - ignore duplicate `event_id`
3. Add logging and error handling
   - dead-letter or rejected-event log file/table
4. Write MVP SQL query pack
   - Top selling containers (by units sold)
   - Top revenue containers
   - Current inventory by product
   - Restock frequency by product
   - Daily sales trend
5. Create one demo script
   - run producer -> run consumer -> run queries -> print outputs

### Acceptance Criteria
- End-to-end run from JSONL/Kafka into Postgres is successful.
- Query results return non-empty outputs from loaded sample data.
- Duplicate events are handled safely.

### Definition of Done
- Loader script committed
- Query file committed with at least 4 MVP queries
- Demo steps documented and reproducible

---

## 4-Day Execution Plan

## Day 1 (Infrastructure + Contract)
- Finalize schema contract and event rules
- Bring up Docker Compose (Kafka + PostgreSQL)
- Create topics and DB init script

**Deliverable:** stack running + schema approved

## Day 2 (Data + Validation)
- Build/clean JSONL dataset
- Implement Pydantic validation
- Add simulator producer to publish events

**Deliverable:** valid events flowing into Kafka

## Day 3 (Model + Load)
- Implement SQL model (DDL + constraints)
- Build Kafka consumer/loader to Postgres
- Add idempotency and rejection logging

**Deliverable:** events successfully loaded into DB

## Day 4 (Business Output + Hardening)
- Implement MVP query pack
- Verify outputs for PO demo questions
- Write runbook, finalize PR, prepare sprint demo

**Deliverable:** reproducible demo with business answers

---

## Suggested Sprint Board Structure
Use columns: **Backlog -> To Do -> In Progress -> Review -> Done**

Recommended ticket labels:
- `infra`, `data-contract`, `dataset`, `streaming`, `db-model`, `etl`, `sql`, `documentation`

Each ticket should include:
- Description
- Acceptance criteria
- Definition of done
- Estimate (0.5d, 1d, etc.)
- Owner

---

## MVP Query Set (Starter SQL)
1. Which containers sell the most? (sum of absolute purchase quantity)
2. Which containers generate the most revenue? (sum of price * sold units)
3. When are products sold/restocked? (events by hour/day)
4. Current inventory levels per product/warehouse
5. Low-stock products below threshold

---

## Product Owner Guidance (you are thinking correctly)
- Your priority order is correct: **schema -> infrastructure -> loading -> SQL outputs**.
- Dashboard should wait; business-value SQL first is the right call for Sprint #2.
- Keep scope strict: one clean end-to-end slice beats many half-finished features.
- Define “done” for each part before coding starts to reduce team confusion.

---

## Risks and Mitigations
- Risk: Kafka config issues consume day 1
  - Mitigation: keep compose minimal, use known image versions
- Risk: schema drift between JSONL and DB
  - Mitigation: single schema contract file + validation in pipeline
- Risk: duplicate/invalid events break loads
  - Mitigation: PK on event_id + rejected-event handling
- Risk: no demo-ready output
  - Mitigation: protect day 4 for SQL query outputs and runbook only
