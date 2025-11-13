# SQL Queries

This folder contains all SQL queries used for analysis and data transformation for the project.

The queries are grouped by their purpose and data source:

---

## 1. Main Project (Synthetic Data)

These queries run on the synthetic dataset built for the core Coin Master analysis (KPIs, Retention, Revenue).

* **`daily_kpi_summary.sql`:** The query used to create the pre-aggregated summary table that powers the main dashboard.
* **`retention_cohort.sql`:** The query used to generate the data for the Daily Retention chart.
* **`main_kpis.sql`:** The query used to calculate the main KPIs individually.

---

## 2. Tutorial Funnel Analysis (External Data)

These queries were used for the tutorial funnel analysis, which was based on a separate dataset.

* **`tutorial_query.sql`:** The main query used to analyze the tutorial funnel.
* **`data_exploration.sql`:** Initial queries used for exploring the tutorial dataset.
