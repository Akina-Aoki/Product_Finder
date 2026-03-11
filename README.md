# Product_Finder

Event-driven product/inventory tracking system built with **Python 3.12**, **uv**, and Kafka.

This project is fully reproducible. All contributors use the same Python version and dependency lock file to ensure consistency across machines.

---

# 🧱 Tech Stack & Dependencies

| Package        | Purpose                                     |
| -------------- | ------------------------------------------- |
| kafka-python   | Kafka producer/consumer client              |
| psycopg        | PostgreSQL driver                           |
| psycopg-binary | Binary build of psycopg for easier installs |
| pydantic       | Schema validation for event data            |
| orjson         | Fast JSON parsing (Kafka events)            |
| tenacity       | retrying for kafka connection & DB inserts  |
| structlog      | Structured logging: pipeline observability  |


---

# 📦 Prerequisites

Install uv if needed:

```bash
pip install uv
```

----
## First Time Set-up
1️⃣ Clone the Repository
```
git clone https://github.com/YOUR_USERNAME/Product_Finder.git
```

2️⃣ Install & Pin Python 3.12
In your VSCode/IDE
```
uv python install 3.12
uv python pin 3.12
```

Verify:
```
cat .python-version
```

Expected output:
```
3.12
```

3️⃣ Create Virtual Environment
```
uv venv
```

Activate it: Windows (Git Bash)
```
source .venv/Scripts/activate
```

Mac/Linux
```
source .venv/bin/activate
```

You should now see:
```
(Product_Finder)
```

4️⃣ Install Project Dependencies
- This installs all dependencies from uv.lock.
```
uv sync
```

- ⚠️ Do NOT use pip install.
- Always use for new dependencies.:
```
uv add <package>
```

5️⃣ Verify Environment Isolation

Check Python version:
```
python -V
```

Expected:
```
Python 3.12.x
```

Check interpreter path:
```
python -c "import sys; print(sys.executable)"
```

It must point to:
```
Product_Finder/.venv/...
```

---

## 🐳 Docker Setup (Postgres + Kafka + Kafka UI)

1. Create local env file:

```bash
cp .env.example .env
```

2. Start infrastructure:

```bash
docker compose up -d
```

Services:
- **Postgres**: `localhost:${DB_HOST_PORT}` (default `localhost:5439`, db name `SportWearDB`, container `SportWear_Postgres`)
- **Kafka broker (host access)**: `localhost:29092`
- **Kafka broker (docker-internal)**: `kafka:9092`
- **Kafka UI**: http://localhost:8080

Notes:
- On first start, Postgres runs `sql/init.sql` automatically using `/docker-entrypoint-initdb.d/init.sql`.
- Optional SQL folder mount is available at `/src_sql` inside the Postgres container.
  You can run SQL files manually, for example:

```bash
docker compose exec postgres psql -U ${DB_USER:-postgres} -d ${DB_NAME:-SportWearDB} -f /src_sql/init.sql
```
- If you change `sql/init.sql` and need a clean re-init:

```bash
docker compose down -v
docker compose up -d
```

Stop services:

```bash
docker compose down
```
