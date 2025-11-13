import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid
import pandas_gbq
import logging
from google.cloud import bigquery
import functions_framework
import os

# --- 1. Global Parameters & Setup ---
fake = Faker()
BASE_INSTALLS_PER_DAY = 33

PERSONA_DISTRIBUTION = {
    'Non-Payer': 0.95,
    'Low-Spender': 0.04,
    'High-Spender': 0.01
}

# [!!! NEW V12: Retention Curve Model !!!]
# This is a base curve. We will multiply it by persona.
# Based on your target image (e.g., Day 1 ~25%, Day 7 ~30%, Day 14 ~20%)
BASE_RETENTION_CURVE = {
    1: 0.25,  # Day 1
    2: 0.23,
    3: 0.28,
    4: 0.25,
    5: 0.24,
    6: 0.28,
    7: 0.30,
    14: 0.18,
    21: 0.15,
    30: 0.10
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

# --- [V12] Udpated Schema (with Persona) ---
COLUMNS = [
    'event_timestamp', 'user_pseudo_id', 'session_id', 'event_name', 'platform',
    'app_version', 'country', 'current_village_level', 'spin_cost',
    'spin_outcome_type', 'spin_outcome_value', 'item_cost', 'entry_point',
    'product_id', 'price_usd',
    'attack_target_id', 'raid_target_id', 'invite_method',
    'attribution_source', 'inviter_user_id',
    'persona'  # [!!!] We must save the persona! [!!!]
]

# --- BigQuery Configuration ---
PROJECT_ID = "ppltx-ba-course-guy"
TABLE_ID = "coin_master_project.events"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# [!!!] This decorator turns our script into a Cloud Function [!!!]
@functions_framework.http
def handler(request):
    """
    Main entry point for the Cloud Function.
    This function will be triggered by Cloud Scheduler.
    """
    logger.info("Cloud Function triggered. Starting daily data generation...")

    # We'll simulate "yesterday's" data
    YESTERDAY = datetime.now() - timedelta(days=1)
    YESTERDAY_DATE = YESTERDAY.date()
    YESTERDAY_DATE_STR = YESTERDAY.strftime('%Y-%m-%d')

    all_daily_events = []

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # [!!! NEW V12: Phase 1 - Fetch & Simulate RETURNING Users !!!]
        logger.info(f"Phase 1: Fetching returning users for {YESTERDAY_DATE_STR}...")

        # 1a. Fetch active users from BQ
        returning_user_list = fetch_returning_users(client, YESTERDAY_DATE_STR)

        # 1b. Create the "global pool" of *existing* users for attacks/raids
        # We will add new users to this pool later
        global_user_id_pool = [u['user_pseudo_id'] for u in returning_user_list]

        if not global_user_id_pool:
            global_user_id_pool = ["dummy_user_1"]  # Safety net

        logger.info(f"Found {len(returning_user_list)} potential returning users.")

        # 1c. Simulate their sessions
        returning_events = simulate_returning_users(returning_user_list, YESTERDAY_DATE, global_user_id_pool)
        all_daily_events.extend(returning_events)
        logger.info(f"Generated {len(returning_events)} events for returning users.")

        # [!!! MODIFIED V12: Phase 2 - Simulate NEW Users !!!]
        logger.info(f"Phase 2: Generating new users for {YESTERDAY_DATE_STR}...")

        # 2a. Decide how many new users to create (Your existing logic)
        lambda_roll = random.random()
        if lambda_roll <= 0.80:
            daily_variance = random.randint(10, 20)
        else:
            daily_variance = random.randint(-15, -8)
        TOTAL_USERS_FOR_THIS_DAY = BASE_INSTALLS_PER_DAY + daily_variance
        if TOTAL_USERS_FOR_THIS_DAY < 5: TOTAL_USERS_FOR_THIS_DAY = 5

        # 2b. Create a pool of *potential* inviters (can be any active user)
        inviter_pool = random.sample(global_user_id_pool, k=min(len(global_user_id_pool), 100))
        if not inviter_pool: inviter_pool = ["dummy_inviter"]

        # 2c. Add new user IDs to the global pool *before* simulation
        # so they can be attacked/raided on their first day
        new_user_ids = [str(uuid.uuid4()) for _ in range(TOTAL_USERS_FOR_THIS_DAY)]
        global_user_id_pool.extend(new_user_ids)

        # 2d. Simulate new user sessions
        new_user_events = simulate_new_users(
            new_user_ids,
            YESTERDAY,
            global_user_id_pool,
            inviter_pool
        )
        all_daily_events.extend(new_user_events)
        logger.info(f"Generated {len(new_user_events)} events for {TOTAL_USERS_FOR_THIS_DAY} new users.")

        # [!!! MODIFIED V12: Phase 3 - Write ALL events to BigQuery !!!]
        logger.info(f"\nPhase 3: Creating DataFrame... (Total events: {len(all_daily_events):,})")

        if not all_daily_events:
            logger.warning("No events were generated. Exiting.")
            return "No events generated.", 200

        df = pd.DataFrame(all_daily_events, columns=COLUMNS)

        logger.info("Converting data types...")
        df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
        df['current_village_level'] = df['current_village_level'].astype('Int64')
        df['spin_cost'] = df['spin_cost'].astype('Int64')
        df['spin_outcome_value'] = df['spin_outcome_value'].astype('Int64')
        df['item_cost'] = df['item_cost'].astype('Int64')
        df['price_usd'] = df['price_usd'].astype('float')

        logger.info(f"Phase 4: Appending {len(df):,} rows to BigQuery table: {TABLE_ID}...")

        # [!!!] PROTECTION MECHANISM: 1. DELETE OLD DATA FOR THIS PARTITION [!!!]
        delete_query = f"DELETE FROM `{TABLE_ID}` WHERE DATE(event_timestamp) = '{YESTERDAY_DATE_STR}'"
        delete_job = client.query(delete_query)
        delete_job.result()
        logger.warning(f"Successfully cleared partition for {YESTERDAY_DATE_STR}.")

        # 2. APPEND the fresh data
        pandas_gbq.to_gbq(
            df,
            TABLE_ID,
            project_id=PROJECT_ID,
            if_exists='append',
            chunksize=50000,
            progress_bar=False
        )
        success_message = f"Success! {len(df):,} new events (returning + new) were appended."
        logger.info(success_message)
        return success_message, 200  # Return HTTP OK

    except Exception as e:
        error_message = f"Error in handler: {e}"
        logger.error(error_message, exc_info=True)
        return error_message, 500  # Return HTTP Server Error


# --- [!!! NEW V12 !!!] Helper function to fetch returning users ---
def fetch_returning_users(client, yesterday_str):
    """
    Queries BQ to get a list of active users who might return.
    NOTE: This query scans the last 30 days. On a large dataset,
    this can be slow/expensive without proper partitioning.
    """
    query = f"""
    WITH LatestUserData AS (
      SELECT
        user_pseudo_id,
        DATE(MIN(event_timestamp)) AS install_date,
        -- Use ARRAY_AGG to get the most recent non-null values
        ARRAY_AGG(persona IGNORE NULLS ORDER BY event_timestamp DESC LIMIT 1)[OFFSET(0)] as persona,
        ARRAY_AGG(current_village_level IGNORE NULLS ORDER BY event_timestamp DESC LIMIT 1)[OFFSET(0)] as current_village_level,
        MAX(DATE(event_timestamp)) as last_active_date
      FROM
        `{TABLE_ID}`
      WHERE
        -- Scan the last 30 days for active users
        DATE(event_timestamp) >= DATE_SUB(PARSE_DATE('%Y-%m-%d', @yesterday), INTERVAL 30 DAY)
      GROUP BY
        1
    )
    SELECT
      *,
      DATE_DIFF(PARSE_DATE('%Y-%m-%d', @yesterday), install_date, DAY) AS user_age_days
    FROM
      LatestUserData
    WHERE
      -- Only get users who installed *before* yesterday
      install_date < PARSE_DATE('%Y-%m-%d', @yesterday)
      -- And who were active recently (e.g., in the last 35 days)
      -- This simulates natural churn.
      AND DATE_DIFF(PARSE_DATE('%Y-%m-%d', @yesterday), last_active_date, DAY) < 35
    """

    # Set query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("yesterday", "STRING", yesterday_str),
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        # Convert BQ rows to a list of dictionaries
        user_list = [dict(row.items()) for row in results]
        return user_list
    except Exception as e:
        logger.error(f"Failed to fetch returning users: {e}")
        return []


# --- [!!! NEW V12 !!!] Helper function to simulate returning users ---
def simulate_returning_users(user_list, yesterday_date, global_user_id_pool):
    returning_events = []
    for user in user_list:
        # 1. Get user state
        user_age = user['user_age_days']
        persona = user['persona'] if user['persona'] else 'Non-Payer'  # Default if missing

        # 2. Get base retention prob from our curve
        base_prob = BASE_RETENTION_CURVE.get(user_age, 0.05)  # 5% long-tail retention

        # 3. Adjust probability by persona
        retention_multiplier = 1.0
        if persona == 'Low-Spender':
            retention_multiplier = 1.2
        elif persona == 'High-Spender':
            retention_multiplier = 1.5

        prob_to_return = base_prob * retention_multiplier

        # 4. Roll the dice
        if random.random() < prob_to_return:
            # This user returns!

            # Re-create the 'user' dictionary for generate_session_events
            # We must update the village level from the BQ query
            user_state_dict = {
                'user_pseudo_id': user['user_pseudo_id'],
                'persona': persona,
                'country': user.get('country', random.choice(COUNTRIES)),  # BQ might not have this
                'platform': user.get('platform', random.choice(PLATFORMS)),  # BQ might not have this
                'current_village_level': user.get('current_village_level', 1),  # Get latest level
                'is_churned': False,  # They are not churned today
                'sent_invites': 0  # We don't track this state
            }

            # Generate 1-3 sessions for this returning user
            num_sessions = 1
            if persona == 'Low-Spender': num_sessions = random.randint(1, 2)
            if persona == 'High-Spender': num_sessions = random.randint(1, 3)

            base_time = datetime.combine(yesterday_date, datetime.min.time())

            for i in range(num_sessions):
                session_id = str(uuid.uuid4())
                session_time = base_time + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )

                # Create the 'app_open' event for the new session
                returning_events.append(create_event(user_state_dict, session_id, 'app_open', session_time,
                                                     {'attribution_source': 'organic'}))

                # Generate the rest of the session events
                session_events = generate_session_events(user_state_dict, session_time, global_user_id_pool)
                returning_events.extend(session_events)

                # IMPORTANT: The user's village level might have updated *inside* generate_session_events
                # We update it here so the *next* session (if any) has the correct level
                user['current_village_level'] = user_state_dict['current_village_level']

    return returning_events


# --- [!!! NEW V12 !!!] Refactored function for NEW users ---
def simulate_new_users(new_user_ids, yesterday_datetime, global_user_id_pool, inviter_pool):
    new_user_events = []

    for user_id in new_user_ids:
        # Create the new user dict
        user = {
            'user_pseudo_id': user_id,
            'persona': np.random.choice(list(PERSONA_DISTRIBUTION.keys()), p=list(PERSONA_DISTRIBUTION.values())),
            'country': random.choice(COUNTRIES),
            'platform': random.choice(PLATFORMS),
            'current_village_level': 1,  # All new users start at level 1
            'is_churned': False,
            'sent_invites': 0
        }

        # [This is your existing logic, slightly modified]
        session_id = str(uuid.uuid4())
        install_time = datetime.combine(yesterday_datetime.date(), datetime.min.time()) + timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # 1. Determine their attribution source
        attr_source = np.random.choice(ATTRIBUTION_SOURCES, p=[0.4, 0.25, 0.25, 0.1])  # 10% come from friend invites
        inviter_id = None
        if attr_source == 'friend_invite':
            inviter_id = random.choice(inviter_pool)

        # 2. Create the FIRST app_open event (The Install)
        new_user_events.append(create_event(user, session_id, 'app_open', install_time, {
            'attribution_source': attr_source,
            'inviter_user_id': inviter_id
        }))

        # 3. Generate their first session's events
        session_events = generate_session_events(user, install_time, global_user_id_pool)
        new_user_events.extend(session_events)

        # 4. [Optional] Decide if they play *more* sessions today
        play_chance = 0
        if user['persona'] == 'Low-Spender':
            play_chance = 0.3
        elif user['persona'] == 'High-Spender':
            play_chance = 0.5

        if random.random() < play_chance:
            num_sessions = random.randint(1, 2)
            for i in range(num_sessions):
                session_time = install_time + timedelta(minutes=random.randint(30, 180))
                session_id = str(uuid.uuid4())
                new_user_events.append(
                    create_event(user, session_id, 'app_open', session_time, {'attribution_source': 'organic'}))
                session_events = generate_session_events(user, session_time, global_user_id_pool)
                new_user_events.extend(session_events)

    return new_user_events


# --- Helper functions (must be defined for the handler to use) ---

def create_event(user, session_id, name, timestamp, overrides={}):
    # [!!! MODIFIED V12: Now includes persona !!!]
    event_row = {col: None for col in COLUMNS}
    event_row.update({
        'user_pseudo_id': user['user_pseudo_id'], 'session_id': session_id,
        'platform': user['platform'], 'app_version': random.choice(APP_VERSIONS),
        'country': user['country'], 'current_village_level': user['current_village_level'],
        'event_timestamp': timestamp, 'event_name': name,
        'persona': user.get('persona', 'Non-Payer')  # Add persona
    })
    event_row.update(overrides)
    return event_row


def generate_session_events(user, session_timestamp, user_id_list):
    # [!!! MODIFIED V12: Ensure user_id_list is not empty !!!]
    if not user_id_list:
        user_id_list = ["dummy_target"]  # Safety net

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

    # [... rest of your generate_session_events function is unchanged ...]
    # [... it's good as-is, I am omitting it here for brevity ...]
    # [... just make sure the user_id_list is passed correctly ...]

    # --- (Your existing logic for spins, attacks, raids...) ---
    for _ in range(num_spins):
        if len(events_in_session) > 500: break
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

    # [!!!] IMPORTANT: Update the user's village level state [!!!]
    if random.random() < (0.1 + (0.3 * (user['persona'] == 'High-Spender'))):
        user['current_village_level'] += 1

    events_in_session.append(create_event(user, session_id, 'app_close', current_time))
    return events_in_session