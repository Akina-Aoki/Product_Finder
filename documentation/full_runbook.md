# Full Runbook: From `git clone` to Supabase + Evidence Dashboard

This guide is the **full end-to-end flow** for a new person opening the project for the first time.

It covers:
1. Local setup after clone
2. Generating ETL input data
3. Cleaning/transformation
4. Loading to Supabase
5. Running Kafka + API + consumer
6. Running Evidence dashboard (for teacher demo)
7. Validation queries in Supabase

---

## 0) Quick architecture (what you are running)

- Python scripts generate and clean CSV files.
- Supabase stores both `staging` tables and `refined` materialized views.
- Docker runs:
  - FastAPI producer (`app`) on port `8000`
  - Kafka broker + Kafka UI
  - Consumer service that reads Kafka and writes to Supabase
- Evidence (`evidence_app`) reads from Supabase and shows dashboards.

---

## 1) Prerequisites (install once)

### Required tools
- Git
- Python 3.12
- `uv`
- Docker + Docker Compose
- Node.js 20+ and npm
- `psql` CLI (PostgreSQL client)

### Verify tools
```bash
git --version
python --version
uv --version
docker --version
docker compose version
node --version
npm --version
psql --version
```

---

## 2) Clone and open the project
- [Repository Setup](documentation/kafka_and_etl/setup.md)

```bash
git clone <YOUR_REPO_URL>
cd Product_Finder
```

Use this repo root as your working directory for all commands.

---

## 3) Python environment setup

```bash
uv python install 3.12
uv python pin 3.12
uv venv
source .venv/bin/activate
uv sync
```

> On Windows Git Bash, use `source .venv/Scripts/activate`.

Confirm interpreter:
```bash
python -c "import sys; print(sys.executable)"
```

---

## 4) Add environment variables

Create a `.env` file in project root:

```bash
cat > .env <<'ENV'
# Supabase direct Postgres connection (replace values)
DB_URL=postgresql://postgres.<project_ref>:<password>@aws-1-<region>.pooler.supabase.com:6543/postgres

# Optional helper variable for psql commands
SUPABASE_DB_URL=postgresql://postgres.<project_ref>:<password>@aws-1-<region>.pooler.supabase.com:6543/postgres
ENV
```

Load env in current shell:
```bash
set -a
source .env
set +a
```

> Keep `.env` private. Do not commit credentials.

---

## 5) Generate source data + ETL outputs

Run from project root.

### 5.1 Generate dirty products (extract input)
```bash
python scripts/generate_dirty_csv.py
```
Creates: `data/raw/products_dirty.csv`

### 5.2 Transform + clean products
```bash
python scripts/transform.py
```
Creates:
- `data/processed/products_clean.csv`
- `data/processed/products_rejected.csv`

### 5.3 Generate historical orders/items/inventories
```bash
python scripts/generate_sales_csv.py
```
Creates:
- `data/raw/orders.csv`
- `data/raw/items.csv`
- `data/raw/inventories.csv`

---

## 6) Load everything into Supabase
If all fails, CONTACT RIKARD OR AIRA TO GRANT YOU ACCESS TO THE DB
- https://github.com/RikardOledal
- https://github.com/Akina-Aoki

### 6.1 Create schemas/tables/views/functions
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/01_create_tables.sql
```

### 6.2 Seed staging tables from local CSVs
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/04_seed_from_local_csv.sql
```

### 6.3 Reset sequences after seed
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/02_reset_sequences.sql
```

### 6.4 Configure refresh cron (one-time per environment)
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/03_supabase_cron_setup.sql
```

### 6.5 Force one immediate refined refresh now
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/refresh.sql
```

---

## 7) Start streaming services (Kafka + API + consumer)

From project root:

```bash
docker compose up -d --build
```

Check status:
```bash
docker compose ps
```

Check logs:
```bash
docker compose logs -f app
docker compose logs -f consumer
docker compose logs -f kafka
```

Endpoints:
- API: `http://localhost:8000/docs`
- Kafka UI: `http://localhost:8080`

---

## 8) Send a test sale event (prove pipeline works)
- [Test 2: New Product Feature](documentation/test/02_test_newproduct.md)


```bash
curl -X POST "http://localhost:8000/api/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 999001,
    "event_type": "sale",
    "timestamp": "2026-03-27T10:00:00Z",
    "store_id": 1,
    "items": [
      {"product_id": 1, "price": 49.99, "quantity": 1},
      {"product_id": 2, "price": 79.99, "quantity": 2}
    ]
  }'
```

Then verify new rows in Supabase (SQL editor or `psql`):
```sql
SELECT * FROM staging.orders ORDER BY order_id DESC LIMIT 5;
SELECT * FROM staging.items ORDER BY item_id DESC LIMIT 10;
```

Refresh refined views after streaming inserts:
```sql
SELECT refined.refresh_refined();
```

---

## 9) Run Evidence dashboard (teacher-facing demo)

Open a new terminal:

```bash
cd evidence_app
npm install
npm run sources
npm run dev -- --host 0.0.0.0 --port 3000
```

Open:
- `http://localhost:3000`

If you edited SQL files under `evidence_app/sources/sportwear/*.sql`, run this again before demo:
```bash
npm run sources
```

---

## 10) Open and inspect database in Supabase UI

1. Go to your Supabase project dashboard.
2. Open **SQL Editor**.
3. Run validation queries below.
4. Open **Table Editor** and inspect `staging` and `refined` schemas.

### Recommended validation SQL

```sql
-- Row counts
SELECT COUNT(*) AS products_count FROM staging.products;
SELECT COUNT(*) AS inventories_count FROM staging.inventories;
SELECT COUNT(*) AS orders_count FROM staging.orders;
SELECT COUNT(*) AS items_count FROM staging.items;

-- Data quality checks
SELECT COUNT(*) AS negative_inventory_rows
FROM staging.inventories
WHERE amount < 0;

SELECT o.order_id, o.order_price,
       SUM(i.item_price * i.quantity) AS calculated_total
FROM staging.orders o
JOIN staging.items i ON i.order_id = o.order_id
GROUP BY o.order_id, o.order_price
HAVING o.order_price != SUM(i.item_price * i.quantity);

-- Refined layer checks
SELECT COUNT(*) AS refined_orders FROM refined.orders;
SELECT COUNT(*) AS refined_items FROM refined.items;
```

---

## 11) Demo checklist (fast)

- [ ] ETL files generated in `data/raw` and `data/processed`
- [ ] Supabase migrations + seed completed
- [ ] `staging` tables populated
- [ ] `refined` views refreshed
- [ ] Docker services running (`kafka`, `kafka-ui`, `app`, `consumer`)
- [ ] One live sale sent through API and visible in Supabase
- [ ] Evidence dashboard running at `http://localhost:3000`

---

## 12) Useful reset/re-run commands

### Stop services
```bash
docker compose down -v
```

### Rebuild services
```bash
docker compose up -d --build
```

### Re-run full data generation + reload to Supabase
```bash
python scripts/generate_dirty_csv.py
python scripts/transform.py
python scripts/generate_sales_csv.py
psql "$SUPABASE_DB_URL" -f supabase/sql/01_create_tables.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/04_seed_from_local_csv.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/02_reset_sequences.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/refresh.sql
```

---

## 13) Common issues and fixes

### `connection refused` to Supabase
- Check `DB_URL`/`SUPABASE_DB_URL` values.
- Confirm password/project ref are correct.
- Ensure your network allows outbound port `6543`.

### Consumer starts but no DB writes
- Run `docker compose logs -f consumer`.
- Confirm `DB_URL` is loaded and reachable.
- Confirm tables already exist (`01_create_tables.sql` done).

### Evidence loads but empty charts
- Run `SELECT refined.refresh_refined();` in Supabase.
- Re-run `npm run sources` inside `evidence_app`.
- Confirm `evidence_app/sources/sportwear/connection.yaml` points to the correct Supabase instance.