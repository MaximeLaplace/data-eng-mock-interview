# GitGuardian — Analytics Engineer Interview Script

## Interview: "Python proficiency, SQL proficiency and data analytics skills"

**Duration:** ~90 min
**Tools:** Claude Code, terminal
**Data:** Hosted at `https://YOUR-SITE.netlify.app/` (replace after deploy)

---

## PART 0 — INTERVIEWER BRIEF (for you, Maxime)

### Setup before the interview

1. Deploy the `netlify-site/` folder to Netlify
2. Replace `YOUR-SITE` in this script with the actual URL
3. Verify the 3 CSV files are accessible: `/raw_organizations.csv`, `/raw_scan_events.csv`, `/raw_incidents.csv`
4. Have a blank terminal ready for her to use Claude Code

### What you're evaluating

| Skill area | Weight | What "good" looks like |
|---|---|---|
| **Clarification & scoping** | 15% | Asks questions, checks the data page, proposes an approach before coding |
| **Python** | 20% | Fetches CSVs, cleans data, loads into a DB — clean and practical |
| **SQL** | 30% | CTEs, window functions, correct aggregation, NULL handling, readable |
| **Analytics thinking** | 20% | Picks meaningful metrics, thinks in layers, mentions quality/testing |
| **Claude Code usage** | 10% | Drives the logic, uses Claude for boilerplate, reviews and iterates |
| **Communication** | 5% | Narrates decisions, flags trade-offs, explains without being asked |

### Your role

- Deliver the prompt casually (2 sentences)
- Answer her questions using the guide below — be helpful but don't steer
- Let her drive the entire session
- Take notes on the scorecard
- Nudge only if stuck >5 min on something

---

## PART 1 — INTRO (2 min)

### INTERVIEWER SAYS:

> "Hey! So this round is about Python, SQL, and analytics. You'll use Claude Code — treat it like your normal workflow. I'll give you a scenario, you build something, and we'll look at the results together at the end. Ready?"

---

## PART 2 — THE PROMPT

### INTERVIEWER SAYS:

> "So we have some raw data from our secret detection platform — scans, incidents, customer info. I've put it up at **[YOUR-SITE.netlify.app](https://YOUR-SITE.netlify.app/)**. Have a look and build me something useful — I want to understand how our customers are doing with secret detection. What's working, what's not, where should we focus."

That's it. She drives from here.

---

## PART 3 — CLARIFICATION PHASE (5-10 min)

**If she starts coding immediately without looking at the data page or asking anything: yellow flag.** Wait 30 seconds, then say: *"Any questions before you dive in?"*

### Questions she should ask (and your answers)

| Her question | Your answer | Why it matters |
|---|---|---|
| "Can I look at the data page first?" | "Of course, go ahead." | Shows she explores before coding |
| "Who's the audience for this?" | "Think VP of Product or Head of Security — they want to know which customers need help, which detectors are most valuable, how fast incidents get resolved." | Shows stakeholder awareness |
| "Should I build a full dbt project or just SQL queries?" | "Whatever lets you show your thinking. I care about the approach and results, not the tooling." | Tests pragmatism |
| "What database should I use?" | "Your choice — whatever you can query with SQL." | Hoping for DuckDB or SQLite |
| "How much time do I have?" | "About an hour for the build, then we'll review together." | |
| "Is the data clean?" | "It's raw data — you tell me." *(smile)* | She should discover issues herself |
| "What metrics matter most to you?" | "That's part of the exercise — what would *you* track?" | Tests analytics intuition |
| "Should I handle all three tables or focus on one?" | "I'd like to see them connected — that's where the interesting stuff is." | Pushes toward JOINs and modeling |

### What you want to hear her say

- "Let me first look at the webpage to understand the schema"
- "I'll fetch the CSVs, load them into DuckDB, then explore the data"
- "I'll start with some data profiling to see what's in there"
- "I'll build a clean staging layer, then write analysis queries on top"
- "For the business side, I'm thinking MTTR, incident severity breakdown by plan type, detector effectiveness..."

---

## PART 4 — WORK SESSION (55-65 min)

### What she should naturally build

No task list given — but a strong candidate will organically do:

**Step 1 — Fetch & load (~10 min)**
- Read the web page, understand the schema
- Use Python (requests/urllib) to download the 3 CSVs
- Load them into DuckDB (ideal) or SQLite or pandas
- Do a first look: row counts, column types, sample rows

**Step 2 — Data profiling & cleaning (~10 min)**
- Discover the data quality issues:
  - Duplicate rows in all 3 tables
  - Whitespace in org names
  - Mixed-case "Business" vs "business" in plan_type
  - Empty strings in industry, employee_count, severity, repo_id
  - Negative/zero duration_ms
  - Future scan date (2027)
  - resolved_at before detected_at (3 rows)
  - "closed" status (not in expected values: open/resolved/ignored)
  - resolved_at set but status is "open" (2 rows)
- Create clean staging tables/views

**Step 3 — Modeling & analysis (~20-25 min)**
- Join tables together (incidents → scans → orgs)
- Build analytical queries:
  - **MTTR** (mean time to resolution) by severity, by plan type
  - **Incident volume** trends over time (weekly/monthly)
  - **Detector effectiveness** — which detectors find the most critical secrets?
  - **Customer health** — which orgs have the most unresolved critical incidents?
  - **Plan type analysis** — do enterprise customers resolve faster?
  - Something creative she comes up with

**Step 4 — Validation & output (~5-10 min)**
- Sanity checks (row counts, NULL checks, value ranges)
- Clean output she can walk you through

### Data quality issues cheat sheet (the 10 traps)

She doesn't need to find ALL of them, but finding 5+ is a green flag.

| # | Issue | Where | How to spot it |
|---|---|---|---|
| 1 | **Duplicate rows** | All 3 tables | COUNT(*) vs COUNT(DISTINCT pk) |
| 2 | **Whitespace in names** | raw_organizations.org_name | TRIM() or visual inspection |
| 3 | **Mixed-case plan_type** | raw_organizations (one "Business") | SELECT DISTINCT plan_type |
| 4 | **Empty industry** | raw_organizations (1 row) | WHERE industry = '' or IS NULL |
| 5 | **Empty employee_count** | raw_organizations (1 row) | Same |
| 6 | **Negative/zero duration_ms** | raw_scan_events (3 rows) | WHERE duration_ms <= 0 |
| 7 | **Future scan date** | raw_scan_events (1 row, year 2027) | MAX(scanned_at) |
| 8 | **Empty repo_id** | raw_scan_events (1 row) | WHERE repo_id = '' |
| 9 | **resolved_at < detected_at** | raw_incidents (3 rows) | WHERE resolved_at < detected_at |
| 10 | **Unexpected status "closed"** | raw_incidents (1 row) | SELECT DISTINCT status |
| 11 | **resolved_at set but status = "open"** | raw_incidents (2 rows) | WHERE resolved_at != '' AND status = 'open' |
| 12 | **Empty severity** | raw_incidents (1 row) | WHERE severity = '' |

### Green flags (take notes)

**Data exploration:**
- Looks at the web page first, reads the schema
- Does `SELECT *` + `COUNT(*)` + `DISTINCT` checks before writing analysis
- Discovers data quality issues organically
- Creates a clean/staging layer before analysis

**SQL quality:**
- Uses CTEs, not nested subqueries
- Window functions (RANK, LAG, ROW_NUMBER) where appropriate
- Correct GROUP BY granularity
- Handles NULLs and empty strings explicitly
- Filters out bad data with clear reasoning

**Analytics thinking:**
- Picks metrics that tell a story (not just random aggregations)
- Thinks about the audience ("a VP would want to see...")
- Connects tables to answer cross-domain questions
- Mentions what she'd add in production (tests, freshness, documentation)

**Claude Code usage:**
- Asks Claude to plan or outline before coding
- Uses Claude for boilerplate (fetching CSVs, DuckDB setup) and drives the SQL herself
- Reviews output, spots errors, iterates
- Doesn't just paste "build me an analytics pipeline" and accept everything

**Communication:**
- Narrates what she's doing: "I'm going to start by profiling the data..."
- Flags issues: "There are some duplicates here, I'll dedup on the primary key"
- Explains trade-offs: "I'm filtering out the future date rather than imputing it because..."

### Red flags

- Doesn't read the web page / schema before coding
- Pastes the whole prompt into Claude: "do this entire thing for me"
- Never looks at the data (no profiling, no sanity checks)
- Misses obvious data quality issues (duplicates, bad dates)
- All queries are basic SELECT/GROUP BY — no window functions, no CTEs
- Can't explain what a query does when asked
- Treats empty strings and NULLs the same (or ignores both)
- No staging layer — runs analysis directly on raw data
- Silent — doesn't explain decisions

### Nudges (only if stuck >5 min)

| Situation | Nudge |
|---|---|
| Doesn't know where to start | "Maybe start by reading that web page and seeing what data is there." |
| Stuck on fetching CSVs | "You could ask Claude to download the CSV files from those URLs and load them into DuckDB." |
| Doesn't profile the data | "Have you checked what's actually in the data? Any surprises?" |
| Doesn't create staging tables | "If this were dbt, would you query the raw tables directly?" |
| Only writes basic queries | "Can you show me something about how things change over time — trends or comparisons?" |
| Can't decide what to analyze | "If you were presenting to the Head of Security, what would they want to know?" |
| Running out of time, no SQL | "Let's make sure we get to the SQL — even if the data loading is simple, I want to see your queries." |

---

## PART 5 — REVIEW & FOLLOW-UP QUESTIONS (10-15 min)

### INTERVIEWER SAYS:

> "Cool, let's look at what you've got. Walk me through what you built."

Let her present her work, then pick 4-5 of these:

#### On data quality:
1. "You cleaned the data — what issues did you find?"
   - She should list several from the cheat sheet above
2. "How did you handle the rows where resolved_at is before detected_at?"
   - **Good:** Filtered them out OR set resolved_at to NULL with a comment explaining why
3. "What data quality tests would you add in production?"
   - **Good:** not_null on PKs, unique on IDs, accepted_values on status/severity, referential integrity between incidents→scans→orgs, freshness checks

#### On modeling:
4. "If this were a dbt project, how would you structure the models?"
   - **Good:** sources → `stg_` (staging, one per raw table) → `int_` (intermediate, joined/enriched) → `fct_`/`dim_` (marts). Mentions materialization strategy.
5. "What's the grain of your main analysis table?"
   - She should clearly say "one row per incident" or whatever she chose
6. "How would you make this incremental — if new data arrives daily?"
   - **Good:** Incremental materialization in dbt, merge on primary key, use `detected_at` as the cursor

#### On SQL:
7. "Can you walk me through this query?" *(point at the most complex one)*
   - She should explain step by step without hesitation
8. "How would you calculate week-over-week change in incident volume?"
   - **Good:** DATE_TRUNC + COUNT + LAG window function
9. "If these tables had 100M+ rows, what would you change?"
   - **Good:** Partitioning (by date), clustering (by org_id), incremental models, pre-aggregation tables

#### On analytics thinking:
10. "What would you put in a Metabase dashboard for the VP of Product?"
    - **Good:** Executive summary (total incidents, MTTR, resolution rate), breakdown by severity, customer health scorecard, detector effectiveness, trends over time
11. "What's missing from this dataset that would make your analysis better?"
    - **Good:** User actions (who resolved it), repo metadata (language, size, public/private), time-series of stars/forks for the repos, alert notification data, false positive rate

#### On Python:
12. "If this ran daily in Dagster, what would the pipeline look like?"
    - **Good:** Asset-based: raw CSVs → staging → marts. Mentions scheduling, retries, observability. Mentions she'd write to Snowflake instead of DuckDB.

---

## PART 6 — SCORING

### INTERVIEWER SAYS:

> "That wraps up the exercise. Do you have any questions for me about the role or the team?"

### Scorecard

| Area | 1 (Fail) | 3 (Pass) | 5 (Excellent) | Score |
|---|---|---|---|---|
| **Clarification** | Coded immediately, no questions | Asked 2-3 questions, explored data page | Thorough scoping, proposed plan, checked schema first | /5 |
| **Python** | Couldn't fetch or load CSVs | Working fetch + load, basic cleaning | Clean code, proper types, handles errors, well-structured | /5 |
| **SQL** | Only SELECT * or broken queries | Correct JOINs, GROUP BY, CTEs, handles NULLs | Window functions, creative metrics, clean readable style | /5 |
| **Data quality** | Missed all issues | Found 3-4 issues, handled them | Found 6+, clean staging layer, explained reasoning | /5 |
| **Analytics thinking** | Random aggregations, no story | Meaningful metrics, audience-aware | Production mindset: testing, incremental, dashboards, layers | /5 |
| **Claude Code** | "Do everything for me" | Used effectively, reviewed output | Strategic prompts, drove the logic, iterated well | /5 |

**Total: /30**

| Score | Verdict |
|---|---|
| 24-30 | Strong hire |
| 18-23 | Hire |
| 12-17 | Borderline |
| <12 | No hire |

---

## APPENDIX A — PRACTICE PLAYBOOK (share with her)

### How to approach this interview

**First 5 minutes — DON'T CODE. Instead:**
1. Open the URL, read the schema on the web page
2. Ask 2-3 clarifying questions (audience, expectations, time)
3. Say out loud: "Here's my plan: I'll fetch the data, profile it, clean it up, then build some analysis queries."

**Minutes 5-15 — Fetch & profile:**
1. Ask Claude: "Download these 3 CSV files from [URLs] and load them into a DuckDB database."
2. Then: "Show me row counts, column types, and a few sample rows for each table."
3. Then: "Check for data quality issues — duplicates, NULLs, unexpected values, date anomalies."
4. **Talk out loud** about what you find: "Interesting, there are some duplicates here..."

**Minutes 15-25 — Clean & stage:**
1. Ask Claude to create staging views/tables that fix the issues you found
2. Review the SQL — make sure you understand the TRIM(), LOWER(), CASE WHEN, dedup logic
3. Say: "In dbt, these would be my staging models — one per source table."

**Minutes 25-50 — Analyze:**
1. Start with the metrics YOU think matter. Say why.
2. Ask Claude for help with syntax, but drive the logic: "I want MTTR by plan type — write me a query that calculates avg resolution time for resolved critical incidents, grouped by plan."
3. Include at least one query with a **window function** (ranking, week-over-week trend, running total)
4. Do a sanity check: "Does this MTTR number make sense given our data?"

**Last 10 minutes — Polish:**
1. Make sure you have clear output for each business question
2. Run everything end-to-end one more time
3. Be ready to explain any query

### Claude Code patterns

| Do this | Not this |
|---|---|
| "Download these 3 CSVs and load into DuckDB" | "Build me an analytics pipeline" |
| "Check for data quality issues in the raw tables" | (skipping profiling entirely) |
| "Write a query for MTTR by severity — only resolved incidents" | "Write all the queries" |
| "This returns 0 rows, check the join condition" | "It's broken, fix everything" |
| "Explain this CTE to me" (to prepare for follow-up questions) | (blindly running code you don't understand) |

### Things to say out loud

- "Let me read the schema first before I start."
- "I'll profile the data to check for quality issues."
- "There are duplicates — I'll dedup on the primary key in my staging layer."
- "The grain of this table is one row per incident."
- "MTTR only makes sense for resolved incidents — I need to filter."
- "In production I'd add dbt tests: unique, not_null, accepted_values, relationships."
- "For a dashboard, I'd show MTTR trends, severity breakdown, and a customer health scorecard."
- "If this were incremental, I'd use detected_at as my cursor and merge on incident_id."

### Gotchas to watch for

1. **Empty strings ≠ NULLs.** The CSVs have empty strings, not SQL NULLs. When loaded into DuckDB, they may stay as empty strings. Use `NULLIF(column, '')` or handle in staging.
2. **Duplicates exist in all 3 tables.** Always dedup in staging.
3. **"closed" is not a valid status.** Only open/resolved/ignored. Decide what to do (map to resolved? filter out?) and explain why.
4. **resolved_at before detected_at** is bad data. Don't just calculate negative MTTR — filter or null it out.
5. **One scan has a future date (2027).** Filter it or flag it — don't silently include it.
6. **GitHub's product is about secrets in code.** Understand what GitGuardian does — a detector finds API keys, passwords, tokens in repos. This context helps you pick meaningful metrics.

---

## APPENDIX B — IDEAL SOLUTION SHAPE (for your evaluation only)

A strong candidate produces roughly:

```python
# 1. Fetch CSVs
import requests, duckdb

urls = {
    "raw_organizations": "https://YOUR-SITE.netlify.app/raw_organizations.csv",
    "raw_scan_events": "https://YOUR-SITE.netlify.app/raw_scan_events.csv",
    "raw_incidents": "https://YOUR-SITE.netlify.app/raw_incidents.csv",
}
# Download and load into DuckDB
```

```sql
-- 2. Staging (clean layer)
CREATE TABLE stg_organizations AS
SELECT DISTINCT
    org_id,
    TRIM(org_name) AS org_name,
    LOWER(plan_type) AS plan_type,
    CAST(signed_up_at AS TIMESTAMP) AS signed_up_at,
    NULLIF(industry, '') AS industry,
    CAST(NULLIF(employee_count, '') AS INTEGER) AS employee_count
FROM raw_organizations;

-- Similar for stg_scan_events (filter duration_ms > 0, future dates, dedup)
-- Similar for stg_incidents (handle bad resolved_at, dedup, map 'closed', handle empty severity)

-- 3. Analysis queries
-- MTTR by plan type (uses JOIN, WHERE, AVG, GROUP BY)
-- Incident trends over time (uses DATE_TRUNC, COUNT, window function with LAG)
-- Top detectors by severity (uses GROUP BY, CASE WHEN or filtered aggregates)
-- Customer health (uses ranking window function, JOIN across all 3 tables)
```

### What distinguishes a 3 from a 5:

| Area | Score 3 | Score 5 |
|---|---|---|
| Data quality | Finds duplicates + NULLs | Finds 6+ issues, explains each, staging layer handles all |
| SQL | Correct GROUP BY and JOINs | Window functions, DATE_TRUNC trends, creative metrics |
| Analytics | Answers obvious questions | Picks metrics a VP would actually care about, tells a story |
| Production thinking | "It works" | "Here's what I'd add: tests, incremental, monitoring" |
