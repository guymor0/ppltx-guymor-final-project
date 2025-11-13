  -- DI - Daily Installs & Viral Installs (Installs by source = "friend_invited")
WITH
  installs_table AS (
  SELECT
    user_pseudo_id,
    DATE(MIN(event_timestamp)) AS install_dt
  FROM
    `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY
    1),

-- By EDA we noticed that their is couple attributes_source for each user
  
  user_first_attribution AS (
  SELECT
    user_pseudo_id,
    FIRST_VALUE(attribution_source) OVER (
        PARTITION BY user_pseudo_id
        ORDER BY event_timestamp ASC
    ) AS install_source
  FROM
      `ppltx-ba-course-guy.coin_master_project.events`
  WHERE
      attribution_source IS NOT NULL
  ),

-- We want only the unique for better efficiency

  unique_user_first_attribution as (
    SELECT
      user_pseudo_id,
      MIN(install_source) as install_source
    FROM user_first_attribution
    GROUP BY 1
  )
SELECT
  a.install_dt,
  COUNT(a.user_pseudo_id) AS DI,
  COUNT(CASE WHEN b.install_source = "friend_invite" THEN user_pseudo_id END) as viral_installs
FROM
  installs_table as a
JOIN unique_user_first_attribution as b
USING(user_pseudo_id)
GROUP BY
  1
ORDER BY
  1;

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

  -- Sessions per Dau

SELECT
  DATE(event_timestamp) AS dt,
  ROUND(COUNT(DISTINCT session_id) / COUNT(DISTINCT user_pseudo_id), 2) as Avg_sessions_per_dau
FROM
  `ppltx-ba-course-guy.coin_master_project.events`
GROUP BY
  1
ORDER BY
  1;

-- Core Actions per DAU

SELECT
  DATE(event_timestamp) AS dt,
  ROUND(COUNT(CASE WHEN event_name in ("spin_action", "attack_performed", "raid_performed", "village_item_upgraded") THEN 1 END) / COUNT(DISTINCT user_pseudo_id), 2) as Avg_core_actions_per_dau
FROM
  `ppltx-ba-course-guy.coin_master_project.events`
GROUP BY
  1
ORDER BY
  1;

-- Level Progression Rate: In Days

WITH user_max_level as (
  SELECT
    user_pseudo_id,
    MAX(current_village_level) as final_level
  FROM `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY 1
),

user_progression_time as (
  SELECT 
    user_pseudo_id,
    current_village_level,
    DATE(MIN(event_timestamp)) as level_up_dt
  FROM `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY 1, 2
),

user_progression_summary as (

SELECT
  a.user_pseudo_id,
  b.final_level,
  MIN(level_up_dt) as start_dt,
  MAX(level_up_dt) as end_dt,
FROM user_progression_time as a
JOIN user_max_level as b
USING(user_pseudo_id)
WHERE b.final_level > 1
GROUP BY 1, 2
)

-- Average Days per level (Weighted Average)

SELECT
  ROUND((SUM(DATE_DIFF(end_dt, start_dt, DAY) + 1)) / SUM(final_level - 1), 2) as avg_days_per_level
FROM user_progression_summary

  -- DR - Daily Revenue & Depositors

SELECT
  DATE(event_timestamp) AS dt,
  SUM(price_usd) AS daily_revenue,
  COUNT(DISTINCT CASE
      WHEN event_name = "purchase_completed" THEN user_pseudo_id
  END
    ) AS daily_depositors,
FROM
  `ppltx-ba-course-guy.coin_master_project.events`
GROUP BY
  1
ORDER BY
  1;

-- Daily Revenue & Daily Depositors & Conversion Rate & ARPDAU & ARPPU 

  SELECT
  DATE(event_timestamp) AS dt,
  SUM(price_usd) AS daily_revenue,
  COUNT(DISTINCT CASE WHEN event_name = "purchase_completed" THEN user_pseudo_id END) AS daily_depositors,
  ROUND(COUNT(DISTINCT CASE WHEN event_name = "purchase_completed" THEN user_pseudo_id END) /
  COUNT(DISTINCT user_pseudo_id), 2) as conversion_rate,
  ROUND(SUM(price_usd) / COUNT(DISTINCT user_pseudo_id), 2) as ARPDAU,
  ROUND(SUM(price_usd) / COUNT(DISTINCT CASE WHEN event_name = "purchase_completed" THEN user_pseudo_id END), 2) as ARPPU
FROM
  `ppltx-ba-course-guy.coin_master_project.events`
GROUP BY
  1
ORDER BY
  1;

-- Total Installs by Country

WITH
  installs_table AS (
  SELECT
    user_pseudo_id,
    MIN(country) AS country,
    DATE(MIN(event_timestamp)) AS install_dt
  FROM
    `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY
    1)
SELECT
  country,
  COUNT(install_dt) as total_installs
FROM
  installs_table
GROUP BY
  1;


