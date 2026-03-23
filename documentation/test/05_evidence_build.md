# 🚀 Runbook: Evidence Dashboard + Docker 

This guide explains **what to run, when to run it, and why it is needed** for your dashboard to work correctly in a Docker environment.

🧩 Quick cheat sheet
```
Start system:
→ docker compose up -d
→ docker exec -it SportWear_Evidence npm run sources

Edit pages:
→ refresh browser
→ if needed: docker compose restart evidence

Edit sources:
→ docker exec -it SportWear_Evidence npm run sources

Fix errors:
→ docker exec -it SportWear_Evidence npm run sources

Reset:
→ docker compose down
→ docker compose up -d --build
→ docker exec -it SportWear_Evidence npm run sources
```

---

## 🟢 1. Start the system (when you open your laptop)

### Step 1: Go to your project folder

### Step 2: Start all services
`docker compose up -d` OR `docker compose up -d --build` if built something new inside the repository.

👉 This starts the entire data platform:

- PostgreSQL → stores your data 🐘
- Kafka ? Kafka UI → handles event streaming 📨
- API → receives data ⚡
- Consumer → writes events to database 🔄
- Evidence → dashboard 📊

### Step 3: Check everything is running
`docker compose ps`

👉 See all containers running and healthy.

### Step 4: Build Evidence data (VERY IMPORTANT)
`docker exec -it SportWear_Evidence npm run sources`

👉 This step:
- Reads your SQL from /sources
- Connects to PostgreSQL
- Builds a data layer for the dashboard
- Without this → dashboard will NOT work ❌

### Step 5: Open dashboard in browser
`http://localhost:3000`


-----

## 🟡 2. When you edit dashboard pages (.md files)

Example in `evidence_app/pages/sales.md`

### What to do
- Save your file
- Refresh browser
- 👉 This works because pages are the UI layer

-❗ If changes do NOT appear
`docker compose restart evidence`

- 👉 This restarts the dashboard service so it reloads your changes.

---

## 🔵 3. When you edit SQL in `/sources/`
Example: `evidence_app/sources/sportwear/data_sales.sql`

### What to do
`docker exec -it SportWear_Evidence npm run sources`

This is required because:
- Sources = data layer
- Evidence must rebuild them before using them

Then
- Refresh browser 🔄

---

## 🔴 4. Common errors and how to fix them
❌ Error: Dashboard stuck / Loading / Timeout

👉 Cause:
- Sources not built
- Data layer missing

✅ Fix
-`docker exec -it SportWear_Evidence npm run sources`
- Then refresh browser

❌ Error: manifest.json not found

👉 Cause: Evidence has no compiled data

✅ Fix
`docker exec -it SportWear_Evidence npm run sources`

---

## 🧱 5. SQLite fix (RARE case)
`docker exec -it SportWear_Evidence npm rebuild sqlite3`
👉 What this does
- Fixes internal database used by Evidence.

👉 When to use it? Only if you see:
- "Cannot find module sqlite3"
- Native errors
- Dashboard still broken after running sources

👉 After running
- `docker exec -it SportWear_Evidence npm run sources`
- Then refresh browser

---

## 🟣 6. Full reset (when nothing works)
```
docker compose down
docker compose up -d --build
docker exec -it SportWear_Evidence npm run sources
```

👉 What this does
- Stops everything
- Rebuilds containers
- Starts fresh system
- Rebuilds Evidence data

---

## ⚠️ 7. Important rules (avoid common mistakes)
- ❌ Do NOT run npm run dev (you are using Docker)
- ❌ Do NOT restart Evidence before running sources
- ❌ Do NOT mix localhost and postgres configs
- ❌ Do NOT run commands too fast one after another

---

## 🧠 8. Simple mental model
```
Docker → runs system 🐳
Evidence → shows dashboard 📊
Sources → prepares data 📦
```
