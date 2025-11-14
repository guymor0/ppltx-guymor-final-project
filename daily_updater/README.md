## Daily Updater & Data Generator

This folder contains the core Python scripts responsible for generating and continuously updating the project's simulated game data.

---

### `main.py` - Daily Update Function

This is the stateful Python script designed to run as a **Google Cloud Function**. Its purpose is to simulate new daily game events (one day at a time) and append them to the existing data.

This script contains the project's **final, most up-to-date logic**. Each time it runs, it:
1.  **Fetches returning users:** Queries BigQuery to find the active user base.
2.  **Simulates retention:** Uses a probability model to decide which users return.
3.  **Simulates new installs:** Generates a new cohort of users.
4.  **Assigns Personas:** Tags all *new* users (`Non-Payer`, `Low-Spender`, `High-Spender`) to model different behaviors.

---

### `generate_data.py` - Initial Data Seeder

This is a **one-time utility script** used to create the project's initial historical dataset (e.g., the first 30 days).

It was run once to simulate a large batch of historical data, establishing the "Day 0" baseline.

**Note:** This script represents an earlier version of the logic. The more advanced daily logic (like 'Persona' assignment) was added later and is found in `main.py`.

---

### `requirements.txt`

Contains the necessary Python packages (e.g., `pandas`, `google-cloud-bigquery`) required to run both scripts.
