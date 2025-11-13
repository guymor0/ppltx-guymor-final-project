CREATE OR REPLACE TABLE `ppltx-ba-course-guy.coin_master_project.daily_kpi_summary`
PARTITION BY event_date
OPTIONS (
  partition_expiration_days = 31, 
  description = "Daily aggregate of ALL KPIs (Activity, Revenue, Installs) for dashboarding, segmented by Country."
)
AS

-- [!!!] CTE 1: User Dimension Table (Installs) [!!!]
-- This logic finds the true install date, country, and source for EVERY user.
-- It uses the complex query we validated earlier.
WITH
  installs_table AS (
  SELECT
    user_pseudo_id,
    DATE(MIN(event_timestamp)) AS install_dt,
    MIN(country) AS install_country 
  FROM
    `ppltx-ba-course-guy.coin_master_project.events`
  GROUP BY 1
  ),
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
  unique_user_first_attribution as (
    SELECT
      user_pseudo_id,
      MIN(install_source) as install_source
    FROM user_first_attribution
    GROUP BY 1
  ),
  -- This is our final user dimension table
  user_dim AS ( 
    SELECT
      a.user_pseudo_id,
      a.install_dt,
      a.install_country,
      b.install_source
    FROM installs_table AS a
    LEFT JOIN unique_user_first_attribution AS b
    USING(user_pseudo_id)
  ),

-- [!!!] CTE 2: Daily ACTIVITY Metrics [!!!]
-- This is your original 'daily_metrics' query
daily_activity_metrics AS (
  SELECT
    DATE(event_timestamp) AS event_date,
    country,
    COUNT(DISTINCT user_pseudo_id) AS dau,
    COUNT(DISTINCT session_id) AS total_sessions,
    COUNT(DISTINCT IF(event_name = 'purchase_completed', user_pseudo_id, NULL)) AS paying_users,
    SUM(IF(event_name = 'purchase_completed', price_usd, 0)) AS daily_revenue,
    SUM(IF(event_name = 'spin_action', spin_cost, 0)) AS total_spins_used,
    COUNT(IF(event_name IN ('attack_performed', 'raid_performed'), 1, NULL)) AS total_social_actions
  FROM
    `ppltx-ba-course-guy.coin_master_project.events`
  WHERE 
    country IS NOT NULL
  GROUP BY 1, 2
),

-- [!!!] CTE 3: Daily INSTALL Metrics [!!!]
-- This calculates the install metrics from our User Dimension table
daily_install_metrics AS (
  SELECT
    install_dt AS event_date,
    install_country AS country,
    COUNT(user_pseudo_id) AS daily_installs,
    COUNT(CASE WHEN install_source = "friend_invite" THEN user_pseudo_id END) as daily_viral_installs
  FROM
    user_dim
  WHERE
    install_country IS NOT NULL
  GROUP BY 1, 2
)

-- [!!!] Final Step: Join Activity and Installs [!!!]
-- We join the two types of daily metrics (Activity vs. Installs)
SELECT
  -- Use COALESCE to handle days with Installs but no Activity, or vice-versa
  COALESCE(act.event_date, inst.event_date) AS event_date,
  COALESCE(act.country, inst.country) AS country,
  
  -- Activity Metrics
  COALESCE(act.dau, 0) AS dau,
  COALESCE(act.daily_revenue, 0) AS daily_revenue,
  COALESCE(act.paying_users, 0) AS paying_users, -- This is your 'daily_depositors'
  
  -- [NEW] Install Metrics
  COALESCE(inst.daily_installs, 0) AS daily_installs,
  COALESCE(inst.daily_viral_installs, 0) AS daily_viral_installs,
  
  -- Derived Metrics
  ROUND(SAFE_DIVIDE(act.daily_revenue, act.dau), 2) AS arpdau,
  ROUND(SAFE_DIVIDE(act.daily_revenue, act.paying_users), 2) AS arppu,
  ROUND(SAFE_DIVIDE(act.paying_users, act.dau), 4) AS conversion_rate,
  ROUND(SAFE_DIVIDE(act.total_sessions, act.dau), 2) AS avg_sessions_per_dau,
  ROUND(SAFE_DIVIDE(act.total_social_actions, act.dau), 2) AS avg_social_actions_per_dau,
  
  -- Raw Numbers
  COALESCE(act.total_spins_used, 0) AS total_spins_used,
  COALESCE(act.total_social_actions, 0) AS total_social_actions
  
FROM
  daily_activity_metrics AS act
FULL OUTER JOIN -- We use FULL JOIN to make sure we don't lose days
  daily_install_metrics AS inst
  ON act.event_date = inst.event_date AND act.country = inst.country;