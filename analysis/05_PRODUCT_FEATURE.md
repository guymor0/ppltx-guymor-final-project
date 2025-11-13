# ✨ Product Feature: The Raid League

## 🥇 The Feature: "The Raid League"

* **The Concept:** A weekly tournament where players compete to earn the most coins exclusively from **Raids**.
* **The Mechanic:** At the start of each week, players are automatically placed into a "Division" of 50 people. Matchmaking is based on their **Village Level** and **Raid History** to ensure fair competition.
* **The Goal:** To finish in the Top 5 of the division.
* **The Reward:** Winners receive a **"Gold Raider Badge"** – a prestige reward (a "Bedge") displayed on their profile for the following week, in addition to standard rewards (spins/coins).

---

## 📈 How We Will Measure It (A/B Test)

We will run an A/B Test (Group A: Control, without the feature; Group B: Treatment, with the feature) and measure:

### Primary KPI:
* **Weekly Retention (W1):** Does the feature give players a reason to return week after week?

### Secondary KPIs:
* **Engagement:** Average Daily Spins and Average Daily Raids. *We expect players to "hunt" for more raids.*
* **Monetization:** Conversion Rate (% of paying users). *We will check if the competition drives more players to purchase spins to win.*

---

## ⚠️ The Risks

| Risk | Description |
| :--- | :--- |
| **Cannibalization** | The feature might "steal" focus from other daily tournaments, potentially leading to a decrease in overall revenue from those events. |
| **Unfairness** | If the matchmaking algorithm isn't accurate (e.g., matching low-spenders with high-spenders), players will feel frustrated and abandon the feature. |
| **Economy Imbalance** | If the rewards are too generous, players will have less incentive to purchase spins, which could hurt overall monetization. |

---

## 🔬 A/B Test Execution (Simulated Data Analysis)

* **Feature:** "The Raid League"
* **Primary KPI:** Weekly Retention (W1)

### 1. Hypotheses
* **Null Hypothesis ($\mathrm{H}_0$):** The feature has no effect on W1 retention. ($\mathrm{Retention_B} \le \mathrm{Retention_A}$)
* **Alternative Hypothesis ($\mathrm{H}_1$):** The feature improves W1 retention. ($\mathrm{Retention_B} > \mathrm{Retention_A}$)
* **Significance Level:** $\alpha = 0.05$

### 2. Simulated Test Data

| Group | Total Users | Retained Users (W1) |
| :--- | :--- | :--- |
| **Group A (Control)** | 100,000 | 20,000 |
| **Group B (Treatment)** | 100,000 | 22,000 |

### 3. Data Analysis

* **Group A Retention:** $20,000 / 100,000 = 20.0\%$
* **Group B Retention:** $22,000 / 100,000 = 22.0\%$

We see a **2% absolute lift** in retention. A statistical Z-test was performed to determine significance.
* **Statistical Test Result:** $p\text{-value} < 0.001$

### 4. Business Conclusion
* **Analysis:** The $p\text{-value}$ ($<0.001$) is much smaller than our significance level ($\alpha = 0.05$).
* **Decision:** We **reject the null hypothesis** ($\mathrm{H}_0$).
* **Recommendation:** The "Raid League" feature caused a statistically significant improvement in weekly retention. We recommend a **staged rollout** of the feature to all users.
