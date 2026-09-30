"""
Generate realistic mock data for GitGuardian Analytics Engineer interview.
Data quality issues are intentionally baked in — the candidate should find and handle them.
"""

import csv
import random
import uuid
from datetime import datetime, timedelta

random.seed(42)

# --- Config ---
NUM_ORGS = 25
NUM_REPOS = 80
NUM_SCANS = 400
NUM_INCIDENTS = 600

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

PLAN_TYPES = ["free", "team", "business", "enterprise"]
PLAN_WEIGHTS = [0.35, 0.25, 0.25, 0.15]
INDUSTRIES = ["fintech", "healthtech", "saas", "ecommerce", "devtools", "cybersecurity", "edtech"]
SCAN_TYPES = ["initial", "incremental"]
DETECTORS = [
    "AWS Keys", "GitHub Token", "Google API Key", "Slack Webhook",
    "Generic Password", "Private Key", "Database URI", "JWT Secret",
    "Stripe API Key", "SendGrid Key", "Twilio Auth Token",
]
SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHTS = [0.10, 0.25, 0.35, 0.30]
STATUSES = ["open", "resolved", "ignored"]
STATUS_WEIGHTS_BY_SEVERITY = {
    "critical": [0.20, 0.70, 0.10],   # critical gets resolved more
    "high":     [0.30, 0.55, 0.15],
    "medium":   [0.40, 0.35, 0.25],
    "low":      [0.45, 0.20, 0.35],   # low gets ignored more
}

ORG_NAMES = [
    "Acme Corp", "NovaPay", "HealthFirst", "ShopStream", "CodeForge",
    "DataVault", "SecureStack", "CloudNine", "FinLeap", "MediSync",
    "RetailIQ", "DevPulse", "CyberShield", "EduFlow", "PayBridge",
    "LogiTrack", "AppNest", "SkyLedger", "BioGenix", "TradeHub",
    "PixelCraft", "NetGuard", "SmartGrid", "FlowState", "TrustLayer",
]


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_organizations():
    rows = []
    for i in range(NUM_ORGS):
        org_id = f"org_{i+1:03d}"
        name = ORG_NAMES[i]
        plan = random.choices(PLAN_TYPES, weights=PLAN_WEIGHTS, k=1)[0]
        signed_up = random_date(datetime(2020, 1, 1), datetime(2024, 6, 1))
        industry = random.choice(INDUSTRIES)
        employees = random.choice([10, 25, 50, 100, 250, 500, 1000, 2500, 5000])

        # --- Data quality issues ---
        # A few orgs with extra whitespace in name
        if i in (3, 17):
            name = f"  {name} "
        # One org with mixed-case plan type
        if i == 7:
            plan = "Business"
        # One org with NULL industry
        if i == 12:
            industry = ""
        # One org with NULL employee count
        if i == 20:
            employees = ""

        rows.append([org_id, name, plan, signed_up.strftime("%Y-%m-%d %H:%M:%S"), industry, employees])

    # Duplicate row (data quality issue)
    rows.append(rows[5].copy())

    random.shuffle(rows)
    return rows


def generate_scan_events(org_ids):
    rows = []
    repo_ids = [f"repo_{i+1:03d}" for i in range(NUM_REPOS)]
    repo_to_org = {repo: random.choice(org_ids) for repo in repo_ids}

    for i in range(NUM_SCANS):
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        repo_id = random.choice(repo_ids)
        org_id = repo_to_org[repo_id]
        scanned_at = random_date(START_DATE, END_DATE)
        scan_type = random.choices(SCAN_TYPES, weights=[0.15, 0.85], k=1)[0]
        files_scanned = random.randint(10, 5000)
        duration_ms = random.randint(200, 120000)

        # --- Data quality issues ---
        # A few scans with 0 or negative duration
        if i in (15, 88, 201):
            duration_ms = random.choice([0, -150, -1])
        # One scan with a future date
        if i == 42:
            scanned_at = datetime(2027, 3, 15, 10, 30, 0)
        # One scan with NULL repo_id
        if i == 150:
            repo_id = ""

        rows.append([
            event_id, repo_id, org_id,
            scanned_at.strftime("%Y-%m-%d %H:%M:%S"),
            scan_type, files_scanned, duration_ms,
        ])

    # Duplicate event (same event_id)
    dup = rows[30].copy()
    rows.append(dup)

    random.shuffle(rows)
    return rows, repo_to_org


def generate_incidents(scan_events):
    rows = []
    event_ids = [row[0] for row in scan_events if row[0]]  # skip empty

    for i in range(NUM_INCIDENTS):
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        event_id = random.choice(event_ids)
        detector = random.choice(DETECTORS)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS, k=1)[0]
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS_BY_SEVERITY[severity], k=1)[0]
        detected_at = random_date(START_DATE, END_DATE)

        # Resolved_at logic
        resolved_at = ""
        if status == "resolved":
            # Resolution time depends on severity
            if severity == "critical":
                hours = random.randint(1, 48)
            elif severity == "high":
                hours = random.randint(4, 168)
            elif severity == "medium":
                hours = random.randint(24, 720)
            else:
                hours = random.randint(48, 1440)
            resolved_at = (detected_at + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")

        # --- Data quality issues ---
        # A few resolved_at BEFORE detected_at (bad data)
        if i in (23, 156, 312):
            resolved_at = (detected_at - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M:%S")
            status = "resolved"
        # One incident with empty severity
        if i == 99:
            severity = ""
        # One incident with unknown status
        if i == 250:
            status = "closed"  # not in expected values
        # A few incidents with resolved_at but status is still "open"
        if i in (180, 340):
            resolved_at = (detected_at + timedelta(hours=random.randint(1, 100))).strftime("%Y-%m-%d %H:%M:%S")
            status = "open"

        detected_at_str = detected_at.strftime("%Y-%m-%d %H:%M:%S")

        rows.append([
            incident_id, event_id, detector, severity, status,
            detected_at_str, resolved_at,
        ])

    # Duplicate incident
    rows.append(rows[75].copy())

    random.shuffle(rows)
    return rows


def write_csv(filename, headers, rows):
    path = f"netlify-site/{filename}"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  {path}: {len(rows)} rows")


if __name__ == "__main__":
    print("Generating mock data...\n")

    # Organizations
    orgs = generate_organizations()
    org_ids = list(set(row[0] for row in orgs))
    write_csv("raw_organizations.csv", [
        "org_id", "org_name", "plan_type", "signed_up_at", "industry", "employee_count",
    ], orgs)

    # Scan events
    scans, repo_to_org = generate_scan_events(org_ids)
    write_csv("raw_scan_events.csv", [
        "event_id", "repo_id", "org_id", "scanned_at", "scan_type", "files_scanned", "duration_ms",
    ], scans)

    # Incidents
    incidents = generate_incidents(scans)
    write_csv("raw_incidents.csv", [
        "incident_id", "event_id", "detector_name", "severity", "status", "detected_at", "resolved_at",
    ], incidents)

    print("\nDone! Data quality issues baked in:")
    print("  - Duplicate rows in all 3 tables")
    print("  - Whitespace in org names")
    print("  - Mixed-case plan_type")
    print("  - NULL/empty values in industry, employee_count, severity, repo_id")
    print("  - Negative/zero duration_ms")
    print("  - Future scan date (2027)")
    print("  - resolved_at before detected_at")
    print("  - 'closed' status (not in expected values)")
    print("  - resolved_at set but status is 'open'")
