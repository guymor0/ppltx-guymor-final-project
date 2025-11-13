# 📊 Main KPI’s & Data Architecture

## Key Performance Indicators for Coin Master

Here are the essential KPIs for the game, grouped into three main categories for clarity:

---

### 1. Growth: Acquisition & Virality

| Metric | Definition |
| :--- | :--- |
| **Daily Installs (DI)** | The total number of new app installations each day. |
| **Viral Share of Installs** | Measures the effectiveness of the community in driving new users. |
| **Geographic Install Data** | Total number of game installs broken down by country. |

### 2. Core Health: Retention & Engagement

| Metric | Definition |
| :--- | :--- |
| **DAU (Daily Active Users)** | The number of unique players who open the app at least once within a 24-hour period. |
| **Retention Rate (D1, D7, D30)** | The percentage of new players who return to the app on Day 1, Day 7, or Day 30 following their initial installation. |
| **Sessions per DAU** | The average number of times a player opens the app per day, reflecting play frequency. |
| **Core Actions per DAU** | The average number of core game actions (Pushing the button, Stealing, Attacking) a player performs daily, serving as a pulse for engagement. |
| **Level Progression Rate** | The average time (in days) required for a player to complete a level (build all items), indicating the speed of progression. |

### 3. Revenue and Monetization Metrics

| Metric | Definition | Formula |
| :--- | :--- | :--- |
| **Daily Revenue** | The total gross income generated from all in-app purchases within a single day. | |
| **Conversion Rate (% Paying Users)** | The proportion of daily active players who make at least one purchase. | (Daily Paying Users / DAU) |
| **ARPDAU (Average Revenue Per Daily Active User)** | Financial health of a free-to-play game. | (Daily Revenue / DAU) |
| **ARPPU (Average Revenue Per Paying User)** | Indicates the effectiveness of store bundles. | (Daily Revenue / Daily Paying Users) |

---

## 💾 Storing Data Efficiently: The Aggregate Method

The most crucial step to optimizing analysis and cost management is to shift from querying raw logs to using **Pre-Aggregated Data**.

### What is the Method?

The required method is to implement a **Daily Fact Summary Table** (e.g., `daily_kpi_summary`). This table compresses the voluminous, granular log data (the `events` fact table) into a single row per day. By performing complex aggregations (`SUM, COUNT, AVG`) once a day and storing the results, we drastically reduce the computational load for all subsequent reporting.

### Pros and Cons of Pre-Aggregation

| Advantage (Pro) | Disadvantage (Con) |
| :--- | :--- |
| **Query Performance:** Reports load in seconds vs. minutes, as queries scan ~30 rows instead of 400,000+ event logs. | **Limited Granularity:** The data is optimized for KPIs. Granular queries (e.g., filtering by specific device model) still require querying the original, slower `events` table. |
| **Cost Efficiency:** Significantly reduces BigQuery costs by minimizing the total data scanned by reporting tools. | **Data Latency:** The daily refresh means the data is always one day behind (updated only for the previous day's activity). |
| **Stability:** Dashboards are stable and consume less memory. | **ETL Overhead:** Requires an automated Scheduled Query to maintain and update the table daily. |

### Implementation Process (The Daily ETL)

The process is built as a scheduled **CTAS** (`Create Table As Select`) job that runs sequentially after the main data ingestion:

1.  **Ingestion Pre-Requisite:** The main data ingestion bot (Cloud Function) successfully **inserts** the raw logs for the previous day into the partitioned `events` table.
2.  **Transformation (CTAS Job):** A BigQuery Scheduled Query is executed (e.g., at 05:15 AM). This query runs the complete aggregation logic over the entire `events` table.
3.  **Loading:** The query uses `CREATE OR REPLACE` to overwrite the existing `daily_kpi_summary` table with the fresh, calculated metrics.
4.  **Efficiency:** This process only pays for the heavy computation once (`CTAS`), and then all subsequent reporting tools access the small, cheap, and fast `daily_kpi_summary` table.

### Reporting Query Example

The final reporting query becomes simple, fast, and highly readable:

```sql
SELECT
  event_date,
  dau,
  daily_revenue,
  arppu,
  ROUND(total_social_actions / dau, 2) AS avg_social_actions_per_dau -- Simple calculation
FROM
  `ppltx-ba-course-guy.coin_master_project.daily_kpi_summary`
WHERE
  event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY
  event_date DESC;
