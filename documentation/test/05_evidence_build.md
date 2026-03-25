## Evidence Dashboard (Sprint 4)
The Evidence app is in `evidence_app/` and is used as the business-facing analytics layer.

### Run Evidence locally
```bash
cd evidence_app
npm install
npm run sources
npm run dev -- --host 0.0.0.0 --port 3000
```
Then open: `http://localhost:3000`

### When to rebuild Evidence sources
Run `npm run sources` every time you change SQL under `evidence_app/sources/sportwear/`.

---

## Supabase Database Migration (Sprint 4)
Supabase migration SQL is versioned under `supabase/sql/`.

### Migration order
1. `supabase/sql/01_create_tables.sql`
2. `supabase/sql/02_reset_sequences.sql`
3. `supabase/sql/03_supabase_cron_setup.sql`
4. `supabase/sql/refresh.sql` (manual trigger for materialized-view refresh)

`03_supabase_cron_setup.sql` should be executed once per environment to schedule `refined.refresh_refined()` every 15 minutes.

### Example via `psql`
```bash
psql "$SUPABASE_DB_URL" -f supabase/sql/01_create_tables.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/02_reset_sequences.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/03_supabase_cron_setup.sql
psql "$SUPABASE_DB_URL" -f supabase/sql/refresh.sql
```

### Evidence connection
Evidence points to Supabase through `evidence_app/sources/sportwear/connection.yaml`.