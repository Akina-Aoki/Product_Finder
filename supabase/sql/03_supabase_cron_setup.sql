-- ==========================================
-- SUPABASE CRON SETUP (Run manuel one time)
-- ==========================================

SELECT cron.schedule(
    'refresh_refined_views', 
    '*/15 * * * *', 
    'SELECT refined.refresh_refined();'
);