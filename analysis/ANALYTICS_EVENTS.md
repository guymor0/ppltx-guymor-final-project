# 📈 Coin Master Analytics: In-App Events

## 10 The Most Important In-App Events

* **App Open**
* **Screen Viewed**
* **Spin Action**
* **Spin Outcome Received**
* **Village Item Upgraded**
* **Attack Performed**
* **Raid Performed**
* **Store Opened**
* **Purchase Completed**
* **Friend Invite Sent**

---

## 🔑 Defining 7 Key Events (Name, Description, and Key Properties)

### 1. `app_open`
| | |
| :--- | :--- |
| **Description** | This event, triggered when the app starts or resumes, is crucial for tracking **Daily Active Users (DAU)**, user sessions, and retention. |
| **Properties** | `trigger` (String): Indicates the method by which the app was opened (e.g., "push\_notification"). |
| | `source` (String): Identifies the acquisition source for the current session (e.g., "paid\_ad\_campaign\_X"). |

### 2. `screen_viewed`
| | |
| :--- | :--- |
| **Description** | Triggered each time a user navigates to a new primary screen. Crucial for understanding user flow and navigation patterns. |
| **Properties** | `screen_name` (String): The name of the screen currently being viewed (e.g., "spin\_machine"). |
| | `previous_screen_name` (String): The name of the screen the user just exited (e.g., "main\_village"). |

### 3. `spin_action`
| | |
| :--- | :--- |
| **Description** | This event is recorded every time a user taps the 'spin' button, representing the core mechanic of the game's economy. |
| **Properties** | `spin_cost` (Integer): The number of spins consumed in this action, accounting for multipliers (e.g., 1, 3, 10). |
| | `spins_remaining` (Integer): The user's remaining spin balance immediately before this action. |

### 4. `spin_outcome_received`
| | |
| :--- | :--- |
| **Description** | Fired subsequent to a spin to detail the reward received by the user. Critical for balancing the game's economy. |
| **Properties** | `outcome_type` (String): The category of the reward obtained (e.g., "raid"). |
| | `outcome_value` (Integer): The quantity of the reward received (e.g., coins, spins) or a binary indicator (e.g., 1 for a shield). |

### 5. `village_item_upgraded`
| | |
| :--- | :--- |
| **Description** | Logs successful village item construction or upgrades, indicating primary coin usage and core game progression. |
| **Properties** | `village_id` (Integer): The level number of the user's current village (e.g., 5). |
| | `item_name` (String): The specific item that was upgraded (e.g., "statue\_level\_3"). |
| | `item_cost` (Integer): The amount of coins spent for the upgrade (e.g., 1500000). |

### 6. `store_opened`
| | |
| :--- | :--- |
| **Description** | Records each instance a user accesses the in-app purchase store, marking the initial step in the monetization funnel. |
| **Properties** | `entry_point` (String): Describes how the user entered the store (e.g., "out\_of\_spins\_popup"). |
| | `current_balance_spins` (Integer): The user's spin balance at the moment they entered the store (e.g., 0). |

### 7. `purchase_completed`
| | |
| :--- | :--- |
| **Description** | Triggered upon the successful validation of a real-money purchase by the app store. This event represents the key revenue-generating action. |
| **Properties** | `product_id` (String): The unique identifier for the purchased item (e.g., "bundle\_small\_spins\_9.99"). |
| | `price_usd` (Float): The normalized price of the product in USD (e.g., 9.99). |
| | `currency` (String): The local currency in which the transaction occurred (e.g., "EUR"). |

---

## 🌟 General Attributes (Super Properties)

**Yes.** Super Properties, or general attributes, are data recorded once (e.g., at `app_open`) and automatically included with all subsequent user events.

The most crucial general attributes for data analysis are:

* **`user_id`** (String): A persistent and unique identifier for each user, vital for linking all events to a single individual.
* **`platform`** (String): The operating system the user is on (e.g., "iOS", "Android").
* **`app_version`** (String): The installed application version (e.g., "1.150.2"). This is critical for identifying bugs and evaluating the impact of new features.
* **`session_id`** (String): A unique ID generated for each app open, allowing for the grouping and analysis of all events within a single session.
* **`language`** (String): The user's device language setting (e.g., "en", "es", "he").
* **`current_village_level`** (Integer): The user's current village number (e.g., 15). Including this enables segmentation of any event (like `purchase_completed`) based on the user's progression level at that specific moment.
