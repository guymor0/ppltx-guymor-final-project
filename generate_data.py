import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid
from tqdm import tqdm
import pandas_gbq
import logging
from google.cloud import bigquery
import os  # [!!!] הוספנו את זה

# --- [!!!] התיקון הסופי להרשאות [!!!] ---
# שתי השורות האלה אומרות לפייתון להשתמש במפורש בקובץ המפתח
# במקום "לחפש" הרשאות במחשב
SERVICE_ACCOUNT_KEY = r"credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY
# ----------------------------------------------


# --- 1. Global Parameters & Setup ---
fake = Faker()

# [!!!] FAST VERSION: Reduced parameters for a quick test run [!!!]
TOTAL_USERS = 1000  # Reduced from 50,000 for a fast run
DAYS_BACK = 30  # Reduced from 90
# [!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!]

NOW = datetime.now()
START_DATE = NOW - timedelta(days=DAYS_BACK)

PERSONA_DISTRIBUTION = {
    'Non-Payer': 0.95,
    'Low-Spender': 0.04,
    'High-Spender': 0.01
}

APP_VERSIONS = ['1.150.0', '1.150.1', '1.150.2', '1.151.0']
PLATFORMS = ['iOS', 'Android']
COUNTRIES = ['US', 'IN', 'DE', 'GB', 'FR', 'IL', 'JP', 'BR']
PRODUCT_IDS = {
    4.99: 'bundle_small_4.99',
    9.99: 'bundle_medium_9.99',
    19.99: 'bundle_large_19.99',
    49.99: 'bundle_whale_49.99'
}
INVITE_METHODS = ['facebook', 'whatsapp', 'sms', 'contact_list']
ATTRIBUTION_SOURCES = ['organic', 'paid_ad_A', 'paid_ad_B', 'friend_invite']

# --- [V2] Udpated Schema ---
COLUMNS = [
    'event_timestamp', 'user_pseudo_id', 'session_id', 'event_name', 'platform',
    'app_version', 'country', 'current_village_level', 'spin_cost',
    'spin_outcome_type', 'spin_outcome_value', 'item_cost', 'entry_point',
    'product_id', 'price_usd',
    'attack_target_id', 'raid_target_id', 'invite_method',
    'attribution_source', 'inviter_user_id'
]

# --- BigQuery Configuration ---
PROJECT_ID = "ppltx-ba-course-guy"
TABLE_ID = "coin_master_project.events"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_user_pool(n_users):
    user_pool = []
    for _ in tqdm(range(n_users), desc="Creating users"):
        install_date = fake.date_time_between(start_date=START_DATE, end_date=NOW)
        user_pool.append({
            'user_pseudo_id': str(uuid.uuid4()),
            'persona': np.random.choice(list(PERSONA_DISTRIBUTION.keys()), p=list(PERSONA_DISTRIBUTION.values())),
            'country': random.choice(COUNTRIES),
            'platform': random.choice(PLATFORMS),
            'install_date': install_date.date(),
            'current_village_level': 1,
            'last_played': install_date.date(),
            'is_churned': False,
            'sent_invites': 0
        })
    return user_pool


def create_event(user, session_id, name, timestamp, overrides={}):
    event_row = {col: None for col in COLUMNS}
    event_row.update({
        'user_pseudo_id': user['user_pseudo_id'], 'session_id': session_id,
        'platform': user['platform'], 'app_version': random.choice(APP_VERSIONS),
        'country': user['country'], 'current_village_level': user['current_village_level'],
        'event_timestamp': timestamp, 'event_name': name,
    })
    event_row.update(overrides)
    return event_row


def generate_session_events(user, session_timestamp, user_id_list):
    session_id = str(uuid.uuid4())
    events_in_session = []
    current_time = session_timestamp
    current_time += timedelta(seconds=random.randint(5, 15))

    num_spins = 0
    if user['persona'] == 'Non-Payer':
        num_spins = random.randint(10, 40)
    elif user['persona'] == 'Low-Spender':
        num_spins = random.randint(50, 100)
    elif user['persona'] == 'High-Spender':
        num_spins = random.randint(30, 70)

    for _ in range(num_spins):
        if len(events_in_session) > 500:
            break

        spin_cost = random.choice([1, 3, 5, 10])
        events_in_session.append(create_event(user, session_id, 'spin_action', current_time, {'spin_cost': spin_cost}))
        current_time += timedelta(seconds=random.randint(2, 5))
        outcome_type = random.choice(['coins', 'attack', 'raid', 'shield', 'free_spins'])
        outcome_value = 1
        if outcome_type == 'coins':
            outcome_value = random.randint(1000, 100000) * spin_cost
        elif outcome_type == 'free_spins':
            outcome_value = random.choice([5, 10, 25])
        events_in_session.append(create_event(user, session_id, 'spin_outcome_received', current_time,
                                              {'spin_outcome_type': outcome_type, 'spin_outcome_value': outcome_value}))
        current_time += timedelta(seconds=random.randint(1, 3))
        if outcome_type == 'attack':
            events_in_session.append(create_event(user, session_id, 'attack_performed', current_time,
                                                  {'attack_target_id': random.choice(user_id_list)}))
            current_time += timedelta(seconds=random.randint(10, 20))
        if outcome_type == 'raid':
            events_in_session.append(create_event(user, session_id, 'raid_performed', current_time,
                                                  {'raid_target_id': random.choice(user_id_list)}))
            current_time += timedelta(seconds=random.randint(10, 20))
        if random.random() < 0.1:
            cost = random.randint(50000, 500000) * user['current_village_level']
            events_in_session.append(
                create_event(user, session_id, 'village_item_upgraded', current_time, {'item_cost': cost}))
            current_time += timedelta(seconds=random.randint(10, 30))

    if user['persona'] != 'Non-Payer' and random.random() < 0.3:
        events_in_session.append(create_event(user, session_id, 'leaderboard_viewed', current_time))
        current_time += timedelta(seconds=random.randint(5, 15))
    if user['persona'] != 'Non-Payer' and random.random() < 0.1:
        method = random.choice(INVITE_METHODS)
        events_in_session.append(
            create_event(user, session_id, 'friend_invite_sent', current_time, {'invite_method': method}))
        user['sent_invites'] += 1
        current_time += timedelta(seconds=random.randint(10, 20))
    if user['persona'] == 'Low-Spender' and random.random() < 0.05:
        events_in_session.append(
            create_event(user, session_id, 'store_opened', current_time, {'entry_point': 'out_of_spins_popup'}))
        current_time += timedelta(seconds=random.randint(10, 30))
        price = 4.99
        events_in_session.append(create_event(user, session_id, 'purchase_completed', current_time,
                                              {'product_id': PRODUCT_IDS[price], 'price_usd': price}))
        current_time += timedelta(seconds=random.randint(5, 10))
    if user['persona'] == 'High-Spender' and random.random() < 0.40:
        events_in_session.append(
            create_event(user, session_id, 'store_opened', current_time, {'entry_point': 'out_of_coins_popup'}))
        current_time += timedelta(seconds=random.randint(5, 20))
        price = random.choice([9.99, 19.99, 49.99])
        events_in_session.append(create_event(user, session_id, 'purchase_completed', current_time,
                                              {'product_id': PRODUCT_IDS[price], 'price_usd': price}))
        current_time += timedelta(seconds=random.randint(5, 10))
    if random.random() < (0.1 + (0.3 * (user['persona'] == 'High-Spender'))):
        user['current_village_level'] += 1
    events_in_session.append(create_event(user, session_id, 'app_close', current_time))
    return events_in_session


def main():
    logger.info("Starting historical data generation...")
    logger.info(f"PROJECT_ID: {PROJECT_ID}, TABLE_ID: {TABLE_ID}")

    logger.info("Step 1: Creating user pool with realistic personas...")
    user_pool = create_user_pool(TOTAL_USERS)
    user_id_list = [u['user_pseudo_id'] for u in user_pool]

    logger.info(f"Step 2: Running daily simulation for {DAYS_BACK} days...")

    all_events = []  # We use one big list for the 30-day load

    for day in tqdm(pd.to_datetime(pd.date_range(START_DATE, NOW)),
                    desc=f"Running daily simulation ({DAYS_BACK} days)"):

        inviter_pool = [u['user_pseudo_id'] for u in user_pool if u['sent_invites'] > 0 and not u['is_churned']]
        if not inviter_pool:
            inviter_pool = [random.choice(user_id_list)]

        for user in user_pool:
            if user['install_date'] == day.date():
                session_id = str(uuid.uuid4())
                install_time = day + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                attr_source = np.random.choice(ATTRIBUTION_SOURCES, p=[0.4, 0.25, 0.25, 0.1])
                inviter_id = None
                if attr_source == 'friend_invite': inviter_id = random.choice(inviter_pool)
                all_events.append(create_event(user, session_id, 'app_open', install_time,
                                               {'attribution_source': attr_source, 'inviter_user_id': inviter_id}))
                all_events.extend(generate_session_events(user, install_time, user_id_list))
                user['last_played'] = day.date()
                continue

            if user['install_date'] > day.date() or user['is_churned']:
                continue

            days_since_install = (day.date() - user['install_date']).days
            days_since_last_played = (day.date() - user['last_played']).days

            if user['persona'] == 'Non-Payer':
                if days_since_install > 7 and days_since_last_played > 3 and random.random() < 0.2:
                    user['is_churned'] = True
                    continue
                if days_since_install > 30 and days_since_last_played > 7 and random.random() < 0.5:
                    user['is_churned'] = True
                    continue

            play_chance = 0
            if user['persona'] == 'Non-Payer':
                play_chance = 0.25
            elif user['persona'] == 'Low-Spender':
                play_chance = 0.7
            elif user['persona'] == 'High-Spender':
                play_chance = 0.9

            if random.random() < play_chance:
                num_sessions = 1
                if user['persona'] != 'Non-Payer':
                    num_sessions = random.randint(1, (5 if user['persona'] == 'High-Spender' else 3))
                for i in range(num_sessions):
                    session_time = day + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    session_id = str(uuid.uuid4())
                    all_events.append(
                        create_event(user, session_id, 'app_open', session_time, {'attribution_source': 'organic'}))
                    all_events.extend(generate_session_events(user, session_time, user_id_list))
                user['last_played'] = day.date()

    logger.info(f"\nStep 3: Creating final DataFrame... (Total events: {len(all_events):,})")

    if not all_events:
        logger.warning("No events were generated. Exiting.")
        return

    df = pd.DataFrame(all_events, columns=COLUMNS)

    logger.info("Converting data types...")
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    df['current_village_level'] = df['current_village_level'].astype('Int64')
    df['spin_cost'] = df['spin_cost'].astype('Int64')
    df['spin_outcome_value'] = df['spin_outcome_value'].astype('Int64')
    df['item_cost'] = df['item_cost'].astype('Int64')
    df['price_usd'] = df['price_usd'].astype('float')

    logger.info(f"Step 4: Uploading {len(df):,} rows to BigQuery table: {TABLE_ID}...")

    try:
        # We use the 'google-cloud-bigquery' client to run a query
        logger.warning(f"Clearing all existing data from {TABLE_ID}...")

        # [!!!] This will now use the 'credentials.json' file [!!!]
        client = bigquery.Client(project=PROJECT_ID)
        delete_job = client.query(f"DELETE FROM `{TABLE_ID}` WHERE TRUE")
        delete_job.result()  # Wait for the delete to finish
        logger.info("Old data cleared.")

        # Now, upload the new data using pandas_gbq
        pandas_gbq.to_gbq(
            df,
            TABLE_ID,
            project_id=PROJECT_ID,
            if_exists='append',  # We append to the (now empty) partitioned table
            chunksize=50000,
            progress_bar=True
        )
        logger.info(f"\nSuccess! Data was uploaded to {TABLE_ID}")

    except Exception as e:
        logger.error(f"\n--- ERROR ---")
        logger.error(f"Upload to BigQuery failed. Error details: {e}")
        logger.error("\n--- Troubleshooting ---")
        logger.error("1. Is the 'credentials.json' file in the same folder as the script?")
        logger.error(f"2. Does the Service Account ('bq-data-loader') have 'BigQuery Admin' permissions?")
        logger.error(f"3. Does the Table '{TABLE_ID}' exist and did you run the CREATE TABLE SQL script?")


if __name__ == "__main__":
    main()