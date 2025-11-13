# 🪙 Coin Master: End-to-End Data Analytics Project

This project simulates the complete data lifecycle of the mobile game Coin Master. It includes a stateful Python data generator, SQL queries for data warehousing, a 2-page executive dashboard, and in-depth product/analytics case studies.

---

## 1. About Coin Master

### Why I Chose This App:
I selected Coin Master due to its relevance to the gaming company I aspire to work for. My goal is to understand the factors contributing to its success.

### Purpose of the App:
* **From the Player's Perspective:** To provide a highly engaging, social, and casual gaming experience. The core loop is built around the satisfaction of progression (building villages), collection (completing card sets), and social competition (attacking and raiding friends).
* **From the Business Perspective:** To monetize this deep engagement. The app aims to convert users into paying customers who purchase in-app items (like spins or coins) to accelerate their progress.

### Audience Demographics:
The primary audience is predominantly female (69%), with 31% male players. The game is particularly popular among individuals in their 40s. [**Source: canvasbusinessmodel.com**](https://canvasbusinessmodel.com/blogs/target-market/moon-active-target-market)

---

## 2. 🚀 Project Overview & Structure

This project is divided into several key components, each located in its own folder:

* **`/daily_updater`**: Contains the stateful Python data generator that runs as a Google Cloud Function to simulate new installs and returning user behavior.
* **`/queries`**: Contains all SQL queries used for analysis. Please see the **`queries/README.md`** for a detailed breakdown of the queries for each dataset (Main Project vs. Tutorial Analysis).
* **`/analysis`**: Contains all in-depth analysis documents, case studies, and project definitions (formerly `/analysis`).

---

## 3. 📊 Dashboard & In-Depth Analysis

The primary output is a 2-page Looker Studio dashboard powered by a pre-aggregated BigQuery table.

**[Link to Main Looker Studio Dashboard](https://lookerstudio.google.com/reporting/2b6ec579-b5b0-437d-98e7-42799c8c5193)**

### High-Level Case Study (from Dashboard)

A high-level case study based on this dashboard:

**Scenario:** A manager logs in and sees the DAU spiked to 501 on Nov 10th, then crashed to 53 on Nov 11th.

1.  **Finding 1 (Acquisition):** The `Daily Installs` chart shows an identical spike, confirming the DAU spike was **100% driven by new installs**.
2.  **Finding 2 (Conversion):** The `Daily Revenue & Depositors` chart shows **$0 revenue** and **0 paying users** from this cohort.
3.  **Finding 3 (Retention):** The `Daily Retention` cohort chart (Page 2) shows **0% Day 2 Retention** for the "10 Nov" cohort.
4.  **Conclusion:** The campaign achieved 0% Day 1 retention and 0% conversion, strongly suggesting an audience mismatch.
5.  **Action**: Confirm the marketing campaign source and segment the traffic (using the Country Filter) to pinpoint the mismatching audience.

### Full Project Documentation

For a complete breakdown of all analyses, definitions, and case studies, please see the `analysis` folder. Key documents include:

* **[Tutorial Funnel Analysis](analysis/01_TUTORIAL_ANALYSIS.md)**: A separate funnel analysis for the user tutorial (includes link to its own **[dashboard](https://lookerstudio.google.com/reporting/f7f80e26-f2ba-4df3-a111-698ac8b029c1)**)
* **[Analytics Event Definitions](analysis/02_ANALYTICS_EVENTS.md)**: Definitions for all key in-app events.
* **[KPIs & Data Architecture](analysis/03_KPI_DATA_ARCH.md)**: Definitions for all main KPIs and the data architecture.
* **[Dashboard & Case Study Deep Dive](analysis/04_DASHBOARD_ANALYSIS.md)**: The full, in-depth case study of the DAU volatility incident.
* **[Product Feature Analysis (A/B Test)](analysis/05_PRODUCT_FEATURE.md)**: Proposal and analysis for the "Raid League" feature.
