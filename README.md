# Coin Master: End-to-End Data Analytics Project

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
* **`/queries`**: Contains all SQL queries used for analysis, including the logic for the retention cohort chart and the daily KPI summary table.
* **`/analysis`**: Contains all in-depth analysis documents, including the new feature proposal (A/B Test), the KPI definitions, and the dashboard case study.

---

## 3. 📊 Dashboard & Case Study

The final output is a 2-page Looker Studio dashboard.

**[Link to Full Dashboard & KPI Analysis](https://lookerstudio.google.com/reporting/2b6ec579-b5b0-437d-98e7-42799c8c5193)**

A high-level case study based on this dashboard:

**Scenario:** A manager logs in and sees the DAU spiked to 501 on Nov 10th, then crashed to 53 on Nov 11th.

1.  **Finding 1 (Acquisition):** The `Daily Installs` chart shows an identical spike, confirming the DAU spike was **100% driven by new installs**.
2.  **Finding 2 (Conversion):** The `Daily Revenue & Depositors` chart shows **$0 revenue** and **0 paying users** from this cohort.
3.  **Finding 3 (Retention):** The `Daily Retention` cohort chart (Page 2) shows **0% Day 2 Retention** for the "10 Nov" cohort.
4.  **Conclusion:** The campaign achieved 0% Day 1 retention and 0% conversion, strongly suggesting an audience mismatch.
5.  **Action**: Confirm the marketing campaign source and segment the traffic (using the Country Filter) to pinpoint the mismatching audience.

**[Link to Full Case Study & Product Analysis](./analysis/Product_and_Case_Study.md)**

