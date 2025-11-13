# 🧑‍🏫 Tutorial Analysis & Measurement

## 🎯 Why is a Tutorial Essential?

The primary business goal of a tutorial is **user retention**. It achieves this by:

* **Teaching the Core Loop:** Quickly guiding the user to understand the main game mechanics (e.g., spin, earn, build, raid).
* **Driving to the "Aha! Moment":** Leading the user to the first instance of rewarding gameplay (like their first successful raid), which makes them understand why the game is fun.
* **Reducing Friction:** Preventing the confusion or frustration that causes new users to abandon the app.

> A successful tutorial ensures users are engaged and understand the game's value, making them significantly more likely to return.

---

## 📏 What do you need to measure in the tutorial?

The tutorial must be measured as a **funnel** to identify exactly where users are dropping off. The key metrics (KPIs) to measure are:

* **Overall Completion Rate:** The percentage of users who start the tutorial and successfully complete the final step. This is the main metric for the funnel's overall success.
* **Step-by-Step Drop-off Rate:** The percentage of users who abandon the tutorial at each specific step. This is critical for identifying the exact points of friction or confusion.
* **Time to Complete (per step):** The average time it takes a user to move from one step to the next. A long duration on a seemingly simple step indicates a "bottleneck" caused by poor UI, a bug, or an unclear instruction.

---

## ⚙️ How do we measure it?

We measure it by implementing an **event-based funnel**. This means firing a specific event every time a user successfully completes a step.

This process relies on two types of data:

1.  **Super Properties:** These are attributes sent with all events to provide general context (like `platform`, `app_version`, `language`).
2.  **Event Properties:** These are attributes specific to the tutorial event itself, providing the critical step-by-step detail (like `step_id` and `step_name`).

By firing an event for each step, we can build a precise funnel to track the user's progression and analyze the KPIs defined above.

### Defining Events for the Tutorial Process

The most effective approach is to define a single, generic event that signifies the successful completion of each step within the entire tutorial funnel. The specific context for each step is provided through event properties. This strategy results in a streamlined, scalable, and powerful method.

#### Event Definition

* **Event Name:** `tutorial_step_completed`

#### Event Properties

The `tutorial_step_completed` event will include the following properties for every step:

| Property | Type | Purpose |
| :--- | :--- | :--- |
| **`step_id`** | Number | A sequential identifier (e.g., 1, 2, 3...) that establishes the exact order of the step in the funnel. |
| **`step_name`** | String | Categorizes the type of action the user performed (e.g., "spin\_action", "open\_village\_shop"). |
| **`time_since_start_ms`** | Number | The elapsed time in milliseconds from the beginning of the tutorial. Used to pinpoint bottlenecks. |

#### Example Event Logs

Below is an illustration of how the data for the initial steps would appear:

```json
{
  "event_name": "tutorial_step_completed",
  "properties": {
    "step_id": 1,
    "step_name": "confirm_welcome_popup",
    "time_since_start_ms": 1250
  }
}
{
  "event_name": "tutorial_step_completed",
  "properties": {
    "step_id": 2,
    "step_name": "click_start_button",
    "time_since_start_ms": 3100
  }
}
{
  "event_name": "tutorial_step_completed",
  "properties": {
    "step_id": 6,
    "step_name": "spin_action",
    "time_since_start_ms": 10500
  }
}
{
  "event_name": "tutorial_step_completed",
  "properties": {
    "step_id": 7,
    "step_name": "spin_action",
    "time_since_start_ms": 11800
  }
}
```
---

## 📈 Tutorial Analysis: Successes & Recommendations

> **(Note: The analysis and accompanying dashboard in this section utilize a synthetic dataset.)**  
> A funnel chart is recommended for effectively visualizing and monitoring the tutorial phase.  
> **The complete analysis and funnel visualization are available in the [Tutorial Funnel Dashboard](https://lookerstudio.google.com/reporting/f7f80e26-f2ba-4df3-a111-698ac8b029c1).**

### Observations:

* **High Completion:** 82.15% of users complete the tutorial, proving its fundamental effectiveness.
* **Consistent Drop-off:** A steady 2-3% user "leak" at each step suggests tutorial length causes fatigue.
* **Effective Improvements:** Newer app versions show increased completion rates, confirming successful iterative changes.

### Conclusion & Recommendations:

* Team's iterative improvements are reducing drop-off. **Continue and amplify these strategies.**
* **Validate & Continue Iterations:** Our data supports continued refinement, focusing on small friction points.
* **Analyze Successful Changes:** Identify specific UI/UX changes in the newest app version to understand performance drivers and apply principles elsewhere.
