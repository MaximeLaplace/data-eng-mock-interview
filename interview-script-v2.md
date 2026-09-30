# Interview Script v2 — Customer Health & Engagement (Self-practice)

## The prompt

> "We're trying to understand which customers are healthy and which ones might churn. We have some data about our customers, how they use the product, and their support tickets. I've put it at **[YOUR-SITE-V2.netlify.app](https://YOUR-SITE-V2.netlify.app/)**. Build me something that helps us figure out where to focus."

---

## What this tests (same skills as v1, different angle)

| v1 (Secret Detection) | v2 (Customer Health) |
|---|---|
| Incident resolution (MTTR) | Support ticket resolution (MTTR) |
| Severity breakdown | Priority breakdown |
| Detector effectiveness | Feature adoption |
| Customer plan analysis | Churn analysis + MRR impact |
| Weekly incident trends | Daily/weekly usage trends |

**New concepts tested in v2:**
- Churn analysis (combining usage + support + subscription data)
- Revenue metrics (MRR at risk, revenue by segment)
- Feature adoption & engagement scoring
- Larger dataset (~7K usage rows — tests if she handles volume)

---

## Clarification guide

| Her question | Your answer |
|---|---|
| "What do you mean by 'healthy'?" | "That's part of the question — how would you define a healthy customer?" |
| "Should I build a churn model?" | "Not a prediction model — more like identify signals. Which customers look at risk and why?" |
| "How should I combine the three datasets?" | "That's up to you. They all share customer_id." |
| "What's the time period?" | "The data covers Q1 2025 — January through March." |
| "Who would use this?" | "Think VP of Customer Success — they want to know who to call this week." |

---

## Data quality issues (cheat sheet)

| # | Issue | Table | Detail |
|---|---|---|---|
| 1 | Duplicate rows | All 3 | One dup per table |
| 2 | Whitespace in company_name | raw_customers | Leading/trailing spaces |
| 3 | Mixed-case region | raw_customers | "EU-West" vs "eu-west" |
| 4 | Negative MRR | raw_customers | 1 row with -199 |
| 5 | Empty acquisition_source | raw_customers | 1 row |
| 6 | Seats = 0 | raw_customers | 1 row (doesn't make sense) |
| 7 | Future signup (2026) | raw_customers | 1 row |
| 8 | Free plan with MRR > 0 | raw_customers | Possible 1 row (inconsistency) |
| 9 | Negative event_count | raw_daily_usage | 3 rows |
| 10 | Empty customer_id | raw_daily_usage | 2 rows |
| 11 | Date outside range | raw_daily_usage | 1 row (Nov 2024) |
| 12 | Feature name typo | raw_daily_usage | "dashbord_view" (3 rows) |
| 13 | resolved_at < created_at | raw_support_tickets | 2 rows |
| 14 | Satisfaction out of range | raw_support_tickets | 0, 6, and -1 |
| 15 | Empty category | raw_support_tickets | 1 row |
| 16 | Unknown priority "urgent" | raw_support_tickets | 1 row |

---

## What a strong solution looks like

### Step 1 — Fetch & profile
- Download 3 CSVs, load into DuckDB
- Row counts, distinct checks, value distributions
- Discover at least 5-6 data quality issues

### Step 2 — Clean & stage
```sql
-- stg_customers: TRIM names, LOWER region, filter negative MRR / future signups,
--   NULLIF empty strings, dedup on customer_id
-- stg_daily_usage: filter negative event_count, empty customer_id,
--   fix feature typo, dedup, filter out-of-range dates
-- stg_support_tickets: fix bad resolved_at, clamp satisfaction to 1-5,
--   handle 'urgent' priority, dedup
```

### Step 3 — Interesting analyses

**Customer health score** (the star query):
```sql
-- For each customer, combine:
--   - Usage intensity: avg daily events over last 30 days
--   - Usage trend: is usage going up or down? (compare last 30 days vs prior 30 days)
--   - Support burden: number of open/critical tickets
--   - Satisfaction: avg CSAT score
--   - → Composite health indicator
```

**MRR at risk:**
```sql
-- Customers who have churned: SUM(mrr) lost
-- Customers showing churn signals (low usage + high ticket volume): SUM(mrr) at risk
```

**Feature adoption:**
```sql
-- Which features are most used by plan type?
-- Which features do churned customers NOT use? (potential churn signal)
-- Feature breadth: how many distinct features does each customer use?
```

**Support analysis:**
```sql
-- MTTR by priority (same concept as v1 but for tickets)
-- Ticket volume by category — where are customers struggling?
-- CSAT by category — which areas disappoint customers?
-- Customers with most open tickets (attention needed)
```

**Trends:**
```sql
-- Weekly usage trends per customer (window function with LAG)
-- Are churned customers' usage declining before churn date?
```

### Key SQL patterns expected
- `DATE_TRUNC('week', date)` for time aggregation
- `LAG()` / `LEAD()` for trend comparison
- `RANK()` / `ROW_NUMBER()` for ranking customers
- `CASE WHEN` for bucketing (health score, engagement tier)
- `LEFT JOIN` to keep all customers (even those with 0 tickets)
- `COALESCE` / `NULLIF` for NULL handling
- `FILTER (WHERE ...)` or `CASE WHEN` inside aggregates

---

## Follow-up questions

#### On analytics:
1. "How did you define 'healthy' vs 'at risk'?"
2. "If you had to pick 5 customers for the CS team to call this week, which ones and why?"
3. "What's the relationship between feature adoption and churn in your data?"

#### On modeling:
4. "If this were dbt, how would you structure the project?"
   - **Good:** sources → stg_ → int_customer_usage_summary → fct_customer_health, dim_customers
5. "How would you make this incremental? New usage data arrives daily."
6. "What grain is your customer health table?"

#### On data quality:
7. "What issues did you find in the data?"
8. "How did you handle the satisfaction scores that were out of range?"
9. "There's a feature name typo in the usage data — did you catch it?"

#### On production:
10. "How would you alert the CS team when a customer's health drops?"
    - **Good:** dbt test + Dagster sensor, or metric threshold in Metabase with alerts
11. "What would you add to make this self-service in Metabase?"

---

## Scorecard

| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| **Clarification** | Jumped in blind | Asked a few questions | Defined "healthy", proposed plan | /5 |
| **Python** | Couldn't load data | Working fetch + load | Clean code, proper staging | /5 |
| **SQL** | Basic SELECTs only | JOINs, GROUP BY, CTEs | Window functions, health score, trends | /5 |
| **Data quality** | Missed everything | Found 4-5 issues | Found 8+, clean staging, explained | /5 |
| **Analytics** | Random queries | Meaningful metrics | Customer health framework, actionable | /5 |
| **Claude Code** | Full delegation | Used well, reviewed | Strategic, drove logic, iterated | /5 |

**Total: /30** (same scale as v1)
