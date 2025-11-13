  -- Retention

WITH installs_table as (
  SELECT
    user_pseudo_id,
    DATE(MIN(event_timestamp)) as install_dt
  FROM `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY 1
),
cohort_size_table as (
  SELECT
    install_dt,
    COUNT(user_pseudo_id) as cohort_size
  FROM installs_table
  GROUP BY 1
),
daily_active_users as (
  SELECT 
    b.install_dt,
    DATE_DIFF(DATE(a.event_timestamp), b.install_dt, DAY) + 1 as day_in_game,
    COUNT(DISTINCT a.user_pseudo_id) as active_users
  FROM `ppltx-ba-course-guy.coin_master_project.events` as a
  JOIN installs_table as b
  ON a.user_pseudo_id = b.user_pseudo_id
  WHERE DATE_DIFF(DATE(a.event_timestamp), b.install_dt, DAY) + 1 IN (1,2,3,4,5,6,7,14,21,28)
  GROUP BY 1,2
)
SELECT
  dau.install_dt,
  dau.day_in_game,
  ROUND(dau.active_users / cs.cohort_size, 2) as retention_rate
FROM daily_active_users as dau
JOIN
cohort_size_table as cs
USING(install_dt)
ORDER BY 1,2