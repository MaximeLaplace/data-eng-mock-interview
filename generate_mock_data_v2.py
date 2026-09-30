"""
Generate mock data for interview v2: SaaS Customer Health & Product Engagement.
Different domain from v1 (secret detection) but tests the same skills.
"""

import csv
import random
import uuid
from datetime import datetime, timedelta

random.seed(99)

# --- Config ---
NUM_CUSTOMERS = 30
NUM_USAGE_DAYS = 90  # 3 months of daily usage data
NUM_SUPPORT_TICKETS = 200

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 3, 31)

PLANS = ["free", "starter", "pro", "enterprise"]
PLAN_WEIGHTS = [0.25, 0.30, 0.25, 0.20]
PLAN_MRR = {"free": 0, "starter": 49, "pro": 199, "enterprise": 899}

REGIONS = ["us-east", "us-west", "eu-west", "eu-central", "apac"]
SOURCES = ["organic", "referral", "sales", "marketing", "partner"]

FEATURES = [
    "dashboard_view", "scan_triggered", "alert_configured",
    "report_exported", "api_call", "user_invited",
    "integration_added", "policy_created", "remediation_started",
]

TICKET_CATEGORIES = ["bug", "feature_request", "billing", "onboarding", "integration", "performance"]
TICKET_PRIORITIES = ["critical", "high", "medium", "low"]
TICKET_PRIORITY_WEIGHTS = [0.08, 0.22, 0.40, 0.30]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]

COMPANY_NAMES = [
    "Vertex Labs", "BluePeak", "Quantum Works", "Halo Security", "Greenline Tech",
    "Nimbus AI", "Ironclad Systems", "Pinecone Data", "Arcadia Cloud", "Sentinel Ops",
    "Fabric IO", "Prism Analytics", "Keystone Dev", "Orbit SaaS", "Relay Platform",
    "Beacon Logic", "Mosaic Code", "Stratos Inc", "Helix Cyber", "Vanguard Tech",
    "Northwind", "Catalyst Labs", "TrueShield", "Polaris Data", "Forefront AI",
    "Apex Digital", "Nebula Systems", "Crestline", "Terraforming Inc", "Basecamp Dev",
]


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_customers():
    rows = []
    for i in range(NUM_CUSTOMERS):
        customer_id = f"cust_{i+1:03d}"
        name = COMPANY_NAMES[i]
        plan = random.choices(PLANS, weights=PLAN_WEIGHTS, k=1)[0]
        mrr = PLAN_MRR[plan]
        signed_up = random_date(datetime(2022, 6, 1), datetime(2024, 12, 1))
        region = random.choice(REGIONS)
        source = random.choice(SOURCES)
        num_seats = random.choice([1, 2, 5, 10, 15, 25, 50, 100])

        # Some enterprise customers have higher MRR (custom pricing)
        if plan == "enterprise":
            mrr = random.choice([899, 1499, 2499, 4999])

        # Churned customers
        churned_at = ""
        is_churned = random.random() < 0.15  # 15% churn rate
        if is_churned and plan != "free":
            churned_at = random_date(datetime(2025, 1, 15), datetime(2025, 3, 31)).strftime("%Y-%m-%d")

        # --- Data quality issues ---
        # Extra whitespace
        if i == 4:
            name = f" {name}  "
        # Mixed-case region
        if i == 11:
            region = "EU-West"
        # Negative MRR (bad data)
        if i == 18:
            mrr = -199
        # NULL source
        if i == 22:
            source = ""
        # Seats = 0 (doesn't make sense)
        if i == 8:
            num_seats = 0
        # Future signup date
        if i == 26:
            signed_up = datetime(2026, 5, 1)
        # Free plan but has MRR (inconsistency)
        if i == 14 and plan == "free":
            mrr = 49

        rows.append([
            customer_id, name, plan, mrr,
            signed_up.strftime("%Y-%m-%d"),
            region, source, num_seats, churned_at,
        ])

    # Duplicate row
    rows.append(rows[7].copy())
    random.shuffle(rows)
    return rows


def generate_daily_usage(customers):
    rows = []
    customer_ids = [row[0] for row in customers]

    # Give each customer a "activity level" to make patterns realistic
    activity_levels = {}
    for cid in customer_ids:
        activity_levels[cid] = random.choice(["high", "medium", "low", "dormant"])

    event_counts = {"high": (10, 80), "medium": (3, 25), "low": (0, 8), "dormant": (0, 1)}

    current = START_DATE
    row_id = 0
    while current <= END_DATE:
        for cid in set(customer_ids):  # deduplicate customer_ids (there's a dup)
            level = activity_levels[cid]
            min_events, max_events = event_counts[level]
            total_events = random.randint(min_events, max_events)

            if total_events == 0:
                # Dormant days — skip (no row = no activity)
                # But occasionally add a row with 0s
                if random.random() < 0.1:
                    feature = random.choice(FEATURES)
                    rows.append([
                        f"usage_{row_id:06d}", cid, current.strftime("%Y-%m-%d"),
                        feature, 0, 0,
                    ])
                    row_id += 1
                continue

            # Distribute events across features
            used_features = random.sample(FEATURES, k=random.randint(1, min(5, len(FEATURES))))
            remaining = total_events
            for j, feature in enumerate(used_features):
                if j == len(used_features) - 1:
                    count = remaining
                else:
                    count = random.randint(1, max(1, remaining - (len(used_features) - j - 1)))
                    remaining -= count

                # session_minutes — rough estimate
                session_min = round(count * random.uniform(0.5, 3.0), 1)

                rows.append([
                    f"usage_{row_id:06d}", cid, current.strftime("%Y-%m-%d"),
                    feature, count, session_min,
                ])
                row_id += 1

        current += timedelta(days=1)

    # --- Data quality issues ---
    # A few rows with negative event counts
    for idx in [45, 890, 2100]:
        if idx < len(rows):
            rows[idx][4] = -1

    # A few rows with NULL customer_id
    for idx in [200, 1500]:
        if idx < len(rows):
            rows[idx][1] = ""

    # One row with a date outside the range
    if len(rows) > 100:
        rows[100][2] = "2024-11-15"

    # Duplicate rows
    if len(rows) > 500:
        rows.append(rows[500].copy())
        rows.append(rows[501].copy())

    # A feature name with a typo
    for idx in [300, 750, 1200]:
        if idx < len(rows):
            rows[idx][3] = "dashbord_view"  # typo

    random.shuffle(rows)
    return rows


def generate_support_tickets(customers):
    rows = []
    customer_ids = [row[0] for row in customers]

    for i in range(NUM_SUPPORT_TICKETS):
        ticket_id = f"ticket_{uuid.uuid4().hex[:10]}"
        customer_id = random.choice(customer_ids)
        category = random.choice(TICKET_CATEGORIES)
        priority = random.choices(TICKET_PRIORITIES, weights=TICKET_PRIORITY_WEIGHTS, k=1)[0]
        created_at = random_date(START_DATE, END_DATE)

        # Status depends on age
        days_old = (END_DATE - created_at).days
        if days_old > 30:
            status = random.choices(["resolved", "closed", "open"], weights=[0.5, 0.35, 0.15], k=1)[0]
        elif days_old > 7:
            status = random.choices(["resolved", "in_progress", "open", "closed"], weights=[0.3, 0.3, 0.25, 0.15], k=1)[0]
        else:
            status = random.choices(["open", "in_progress", "resolved"], weights=[0.5, 0.35, 0.15], k=1)[0]

        # Resolution time
        resolved_at = ""
        if status in ("resolved", "closed"):
            if priority == "critical":
                hours = random.randint(1, 24)
            elif priority == "high":
                hours = random.randint(2, 72)
            elif priority == "medium":
                hours = random.randint(12, 240)
            else:
                hours = random.randint(24, 480)
            resolved_at = (created_at + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

        # Satisfaction score (1-5, only for resolved/closed)
        satisfaction = ""
        if status in ("resolved", "closed") and random.random() < 0.7:
            if priority == "critical":
                satisfaction = random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.20, 0.30, 0.25, 0.10], k=1)[0]
            else:
                satisfaction = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.25, 0.35, 0.25], k=1)[0]

        # --- Data quality issues ---
        # resolved_at before created_at
        if i in (33, 142):
            resolved_at = (created_at - timedelta(hours=random.randint(5, 48))).strftime("%Y-%m-%d %H:%M:%S")
            status = "resolved"
        # Satisfaction score out of range
        if i == 77:
            satisfaction = 0
        if i == 160:
            satisfaction = 6
        # Empty category
        if i == 95:
            category = ""
        # Unknown priority
        if i == 130:
            priority = "urgent"  # not in expected values
        # Resolved but satisfaction is negative
        if i == 45:
            satisfaction = -1

        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")

        rows.append([
            ticket_id, customer_id, category, priority, status,
            created_at_str, resolved_at, satisfaction,
        ])

    # Duplicate ticket
    rows.append(rows[50].copy())

    random.shuffle(rows)
    return rows


def write_csv(filename, headers, rows, output_dir="netlify-site-v2"):
    path = f"{output_dir}/{filename}"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  {path}: {len(rows)} rows")


if __name__ == "__main__":
    import os
    os.makedirs("netlify-site-v2", exist_ok=True)

    print("Generating mock data (v2 — Customer Health)...\n")

    customers = generate_customers()
    write_csv("raw_customers.csv", [
        "customer_id", "company_name", "plan", "mrr", "signed_up_at",
        "region", "acquisition_source", "num_seats", "churned_at",
    ], customers)

    usage = generate_daily_usage(customers)
    write_csv("raw_daily_usage.csv", [
        "usage_id", "customer_id", "date", "feature_name", "event_count", "session_minutes",
    ], usage)

    tickets = generate_support_tickets(customers)
    write_csv("raw_support_tickets.csv", [
        "ticket_id", "customer_id", "category", "priority", "status",
        "created_at", "resolved_at", "satisfaction_score",
    ], tickets)

    print("\nDone! Data quality issues baked in:")
    print("  - Duplicate rows in all 3 tables")
    print("  - Whitespace in company names")
    print("  - Mixed-case region ('EU-West' vs 'eu-west')")
    print("  - Negative MRR (1 row)")
    print("  - Empty acquisition_source (1 row)")
    print("  - Seats = 0 (1 row)")
    print("  - Future signup date 2026 (1 row)")
    print("  - Free plan with MRR > 0 (1 row, if plan landed on free)")
    print("  - Negative event_count (3 rows)")
    print("  - Empty customer_id in usage (2 rows)")
    print("  - Date outside range in usage (1 row)")
    print("  - Feature name typo 'dashbord_view' (3 rows)")
    print("  - resolved_at before created_at in tickets (2 rows)")
    print("  - Satisfaction score out of range: 0, 6, -1")
    print("  - Empty category in tickets (1 row)")
    print("  - Unknown priority 'urgent' (1 row)")
