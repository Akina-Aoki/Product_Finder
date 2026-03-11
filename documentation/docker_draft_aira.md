## 🐳 Docker Setup (Postgres + Kafka + Kafka UI)

1. Create local env file:

```bash
.env
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
- If you change `sql/init.sql` and need a clean re-init:

```bash
docker compose down -v
docker compose up -d
```

Stop services:

```bash
docker compose down
```