# 💰 Coin Master - Daily Dashboard

This dashboard is built using the pre-aggregated `daily_kpi_summary` table to ensure fast loading times and efficiency.

---

## I. 🎯 Daily Pulse Scorecards

| Metric | Visualization | Purpose |
| :--- | :--- | :--- |
| **Today's DAU** | Scorecard | Immediate measure of the active user base health. |
| **Today's Revenue** | Scorecard | Immediate measure of financial performance. |
| **Today's Depositors** | Scorecard | Tracks how many unique users paid today. |
| **Total Installs** | Scorecard | Provides a high-level scale of the total game size. |

## II. 📈 Acquisition Trends

| Metric | Visualization | Purpose |
| :--- | :--- | :--- |
| **Daily Installs & Viral Installs** | Line Chart | Tracks new user volume and compares it to virality (friend invites). |
| **Total Installs by Country** | Geo Map | Identifies the key geographic markets for new installs. |

## III. 📊 Daily Performance Trends

| Metric | Visualization | Purpose |
| :--- | :--- | :--- |
| **Daily Active Users (DAU)** | Line Chart | Monitors the overall user base activity trend over time (growth or decline). |
| **Daily Revenue & Depositors** | Dual-Axis Line Chart | Shows the relationship between total revenue and the number of paying users. |

## IV. ⚙️ Filters

* **Country Filter:** Allows for segmenting the entire dashboard by a specific country.

---

## V. 🧑‍🤝‍🧑 User Behavior Analysis (Page 2)

| Metric | Visualization | Purpose |
| :--- | :--- | :--- |
| **Daily Retention** | Cohort Chart | Tracks user "stickiness" by showing what percentage of new users return on Day 1, 7, 14, etc. This is the core measure of long-term game health. |

---

## 🔎 Case Study: Diagnosing DAU Volatility (Based on this Dashboard)

Here is a scenario that can be solved using this dashboard:

**Scenario:** A manager logs in on Nov 12th and sees the DAU is chaotic. It spiked to 501 on Nov 10th, then crashed to 53 on Nov 11th.

### Step 1: Verify the Problem (Page 1 - KPI Dashboard)

* **Action:** Look at the Daily Active Users chart.
* **Finding:** Confirms the massive spike (501) and subsequent crash (53).
* **Conclusion:** This is a massive, abnormal event.

### Step 2: Cross-Reference with Acquisition (Page 1)

* **Action:** Look at the Daily Installs & Viral Installs chart.
* **Finding:** The daily_installs line (blue) shows an identical spike on the exact same days.
* **Conclusion:** The DAU spike was not from returning users; it was 100% driven by new installs. This was likely a massive marketing campaign.

### Step 3: Check User Quality & Conversion (Page 1)

* **Action:** Look at the Daily Revenue & Depositors chart.
* **Finding:** Both the daily_revenue (blue line) and the paying_users (orange line) remained completely flat at 0.
* **Conclusion:** The campaign brought in hundreds of new users who generated $0 in revenue and had a 0% conversion rate.

### Step 4: Confirm the Retention & Churn (Page 2 - Retention Dashboard)

* **Action:** Switch to Page 2 and look at the Daily Retention chart. Find the install cohort row for "10 Nov 2025".
* **Finding 1:** The row for Nov 10th shows 100% at install (Day 0), but the Day 2 column is 0% (empty).
* **Conclusion 1:** This finding directly explains the DAU crash on Nov 11th. With 0% Day 2 retention, none of the 501 new users returned the following day.
* **Finding 2:** An unusual pattern emerges in the Day 3 column for that same cohort, which shows 23% retention.
* **Conclusion 2:** This suggests that 23% of the cohort "resurrected" on Day 3, despite being completely inactive on Day 2.

### Step 5: Hypothesis and Next Steps

**Hypothesis:** The data strongly suggests a large-scale marketing campaign was initiated on Nov 10th. This campaign successfully drove a high volume of installs (501) but attracted users who did not fit the standard player profile, resulting in 0% conversion and 0% Day 1 retention. The 0% retention is the direct cause of the DAU crash on Nov 11th.

**Next Steps (Investigation):**

1.  **Check with Marketing:** Contact the marketing team to confirm if a new campaign or ad source was launched on Nov 10th.
2.  **Segment by Country:** Use the 'Country' filter on the dashboard to see if this install spike was isolated to a specific region. This will help pinpoint the exact campaign.
3.  **Analyze Day 2:** Investigate the unusual 23% Day 2 retention. This might be linked to a delayed push notification or email campaign targeting these new users.
