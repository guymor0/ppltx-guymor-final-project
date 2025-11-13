## Daily Updater - Python Data Generator
This folder contains the `generate_data.py` script.
This is a stateful Python data generator designed to run as a Google Cloud Function. It simulates daily game events by:
1.  **Fetching returning users:** Queries BigQuery to find active users.
2.  **Simulating retention:** Uses a probability model (`BASE_RETENTION_CURVE`) to decide which users return.
3.  **Simulating new installs:** Generates a new cohort of users each day.
4.  **Assigning Personas:** Tags new users (`Non-Payer`, `Low-Spender`, `High-Spender`) to model different behaviors.
