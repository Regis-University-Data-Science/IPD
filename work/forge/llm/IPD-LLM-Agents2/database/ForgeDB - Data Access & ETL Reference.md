# ForgeDB - Data Access & ETL Reference
## Persistent Storage for Iterated Prisoner's Dilemma with LLM Agents

**Version:** 1.1 (February 22, 2026)  
**Author:** Emily D. Carpenter, Anderson College of Business and Computing, Regis University  
**Project:** GENESIS - General Emergent Norms, Ethics, and Societies in Silico  
**Advisors:** Dr. Douglas Hart, Dr. Kellen Sorauf

---

## Overview

ForgeDB provides a Python interface for importing Iterated Prisoner's Dilemma (IPD) research experiment results into PostgreSQL and querying them as pandas DataFrames. It supports two usage modes:

- **Command Line (CLI)** — Import JSON result files from the terminal
- **Python API** — Query experiment data in scripts and notebooks

The `forge` database (schema `ipd2`) runs on the `platinum` host and is accessible to all FORGE team members.

---

## Prerequisites

- IPD2 Repository has been updated from GitHub (i.e. git pull).
- Python virtual environment has been activated.
- Required packages installed for accessing PostgreSQL (psycopg[binary])
- Researcher has been added to PostgreSQL for DB access.

### Verify Database Access

Confirm you can connect to PostgreSQL and query the `ipd2` schema:
```bash
psql -h platinum -d forge -c "SELECT COUNT(*) FROM ipd2.results"
```

If this returns a count, you're good to go. If you get `permission denied`, verify your PostgreSQL role exists and has schema access:
```bash
# Check if your role exists
sudo -u postgres psql -c "\du $USER"

# If your role is missing, create it
sudo -u postgres createuser $USER

# Grant access to the ipd2 schema
sudo -u postgres psql -d forge -c "GRANT USAGE ON SCHEMA ipd2 TO $USER; GRANT ALL ON ALL TABLES IN SCHEMA ipd2 TO $USER; GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipd2 TO $USER;"
```

---

## Part 1: Command Line — Importing Data

### Import a Single File

```bash
python forgedb.py --import results/episodic_game_20260119_143052.json
```

### Import All JSON Files in a Directory

```bash
python forgedb.py --import results/
```

### Import Using a Glob Pattern

```bash
python forgedb.py --import results/episodic_game_202601*.json
```

### Import Multiple Specific Files

```bash
python forgedb.py --import results/game_001.json results/game_002.json results/game_003.json
```

### Specify a Username for Older Files

Older JSON files created prior to January 27th, 2026, may not contain a `username` field. Use `--username` to set one:

```bash
python forgedb.py --import results/ --username dhart
```

### Import Output

```
Loaded: 12, Skipped: 3, Failed: 0
```

- **Loaded** — Successfully imported into the database
- **Skipped** — Duplicate file (already imported, based on filename and timestamp uniqueness)
- **Failed** — Error during import (check `forgedb.log` for details)

### Logging

All import activity is logged to `forgedb.log` in the same directory as `forgedb.py`.

---

## Part 2: Python API — Connecting and Querying

### Instantiate the Class

```python
from forgedb import ForgeDB

# Default connection (current OS user, platinum host, forge database)
db = ForgeDB()

# Class method signature with default parameters. Provided for informational
#   purposes only.
db = ForgeDB(host='platinum', dbname='forge', user=None)

# NOTE: ALWAYS close the database connection when finished:
db.close()
```

---

### Query Methods

All query methods return a **pandas DataFrame** and accept the same optional filter parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | `str` or `datetime` | Results on or after this date |
| `end_date` | `str` or `datetime` | Results before this date |
| `username` | `str` | Filter by username (case insensitive, wildcard is `%` sign) |
| `filename` | `str` | Filter by result filename (case insensitive, wildcard is `%` sign) |
| `limit` | `int` | Maximum rows to return |

---

#### `get_raw_data()` — Raw JSON and Metadata

Returns experiment metadata with the original raw JSON. Useful for inspecting the source data or reprocessing.

**SQL view:** `ipd2.raw_data_vw`  

**Columns:** `results_id`, `username`, `filename`, `timestamp`, `raw_json`

```python
df = db.get_raw_data(username='dhart')
```

---

#### `get_results()` — Full Detail (All Columns)

Returns ALL data columns in the `forge` DB (except raw_json) with each row representing a single round per agent. This is the most granular view.

**SQL view:**  `ipd2.results_vw`

**Note:** Contains duplicate data across rows (e.g., config values, agent data, and episode details repeat for each agent in each round). Requires grouping for analysis.

Examples:

```python
# get all results for user "janesmith"
df = db.get_results(username='janesmith', limit=50)

# get all results with filename containing string "ep50" for user "dhart"
db.get_results(username='dhart', filename='%ep50%')
```
---

#### `get_summary()` — Experiment Summary

Returns one row per experiment with agent data pivoted to columns. Best for comparing experiments at a high level.

**SQL view:** `ipd2.experiment_summary_vw`  

**Columns:** `results_id`, `username`, `filename`, `timestamp`, `hostname`, `elapsed_time`, `agent_#_host`, `agent_#_model`, `agent_#_total_score`, `agent_#_total_cooperations`, `agent_0_cooperation_rate`, **all** config fields, `system_prompt`, and `reflection_template`.

```python
df = db.get_summary()
print(df[['timestamp', 'agent_0_model', 'agent_0_cooperation_rate',
           'agent_1_model', 'agent_1_cooperation_rate']])
```

---

#### `get_episode_summary()` — Episode-Level Summary

Returns one row per episode with agent data pivoted to columns. Useful for tracking cooperation trajectories across episodes. This query is useful in creating the "scatter plot connected points" chart that allows viewing cooperation rate by episodes.

**SQL view:** `ipd2.episode_summary_vw`  

**Columns:** `results_id`, `username`, `filename`, `timestamp`, `episode`, `agent_#_total_score`, `agent_#_total_cooperations`, `agent_#_coop_rate`, `agent_#_reflection`.

```python
df = db.get_episode_summary(username='dhart', filename='%ep50%')
```
---

#### `get_rounds_summary()` — Round-Level Summary (Pivoted)

Returns one row per round with both agents' data side-by-side (i.e. pivoted from rows to columns). Best for round-by-round comparison of agent behavior.

**SQL view:** `ipd2.rounds_summary_vw`  

**Columns:** `results_id`, `username`, `filename`, `timestamp`, `episode`, `round`, `agent_#_episode_id`, `agent_#_action`, `agent_#_payoff`, `agent_#_ep_cumulative_score`, `agent_#_reasoning`.

```python
df = db.get_rounds_summary(
    username='dhart',
    start_date='2026-01-25',
    end_date='2026-01-26 17:00:00'
)
```
---

#### `get_rounds_detail()` — Round-Level Detail (Per Agent)

Returns one row per round per agent (unpivoted). Similar to `get_results()` but focused on round-level data without config columns.

**SQL view:** `ipd2.rounds_detail_vw`  

**Columns:** `results_id`, `username`, `filename`, `timestamp`, `episode_id`, `agent_idx`, `episode`, `round`, `agent`, `action`, `payoff`, `ep_cumulative_score`, `reasoning`, `ep_score`, `ep_cooperations`, `ep_coop_rate`, `ep_reflection`.

```python
df = db.get_rounds_detail(limit=100)
```
---

### Filter Examples

```python
# All experiments by a specific user
df = db.get_summary(username='dhart')

# Partial match with wildcard
df = db.get_summary(username='%smith%')

# Filename pattern matching
df = db.get_raw_data(filename='%ep50%')

# Date range filter where timestamp is greater or equal to start_date (inclusive)
#    and less than the end_date.
df = db.get_results(
    start_date='2026-01-25',
    end_date='2026-01-26 17:00:00'
)

# Combine filters
df = db.get_episode_summary(
    username='dhart',
    filename='%ep50%',
    start_date='2026-01-25',
    end_date='2026-01-26 17:00:00'
)

# Limit rows (useful for testing)
df = db.get_results(limit=10)
```
---

## Part 3: Custom Ad Hoc Queries

For queries not covered by the built-in methods, use `db.query()` with raw SQL. This returns a list of dictionaries (one per row) which can be converted to a DataFrame.

> **Note:** Unlike the built-in query methods which return a pandas DataFrame directly, 
> `db.query()` returns a list of dictionaries. A DataFrame was not returned to allow the developer
> the most flexibility when interacting with the database in an adhoc capacity.

### Basic Custom Query

```python
import pandas as pd
from forgedb import ForgeDB

db = ForgeDB()

sql = """
    SELECT DISTINCT timestamp, username, agent_host
    FROM ipd2.results_vw
    ORDER BY timestamp
"""

rows = db.query(sql)
df = pd.DataFrame(rows)
print(df.to_string())

db.close()
```

### Custom Query with a WHERE Clause

```python
sql = """
    SELECT DISTINCT timestamp, username, agent_host
    FROM ipd2.results_vw
    WHERE username = 'dhart'
    ORDER BY timestamp
"""

rows = db.query(sql)
df = pd.DataFrame(rows)
```

### Parameterized Custom Query

Use `%(name)s` placeholders with a parameter dictionary to prevent SQL injection:

```python
sql = """
    SELECT results_id, username, timestamp, agent_model
    FROM ipd2.experiment_summary_vw
    WHERE username = %(user)s
      AND timestamp >= %(start)s
    ORDER BY timestamp
"""

rows = db.query(sql, params={'user': 'dhart', 'start': '2026-02-01'})
df = pd.DataFrame(rows)
```

### Available Views for Custom Queries

| View | Description | Grain |
|------|-------------|-------|
| `ipd2.raw_data_vw` | Metadata + raw JSON | 1 row per experiment |
| `ipd2.results_vw` | All columns, fully joined | 1 row per round per agent |
| `ipd2.experiment_summary_vw` | Experiment-level, agents pivoted | 1 row per experiment |
| `ipd2.episode_summary_vw` | Episode-level, agents pivoted | 1 row per episode |
| `ipd2.rounds_summary_vw` | Round-level, agents pivoted | 1 row per round |
| `ipd2.rounds_detail_vw` | Round-level, per agent | 1 row per round per agent |

You can also query the base tables directly: `ipd2.results`, `ipd2.llm_agents`, `ipd2.episodes`, `ipd2.rounds`.

---

### Deleting Data

The ForgeDB Python class does not provide a delete method. This is to safeguard research when interacting through Python. To remove experiment data, connect directly to PostgreSQL and delete rows from the `ipd2.results` table using SQL. The schema uses `ON DELETE CASCADE` to ensure that deletes performed on `ipd2.results` automatically remove all related child rows from `llm_agents`, `episodes`, and `rounds`.
```bash
psql -h platinum -d forge
```
```sql
-- Delete by results_id
DELETE FROM ipd2.results WHERE results_id = 42;

-- Delete by filename
DELETE FROM ipd2.results WHERE filename = 'episodic_game_20260126_172659.json';

-- Delete by username
DELETE FROM ipd2.results WHERE username = 'testuser';

-- Delete by date range
DELETE FROM ipd2.results 
WHERE timestamp >= '2026-01-27' AND timestamp < '2026-01-28';
```

> **Caution:** Deletes are permanent and cascade to all child tables. Verify your WHERE clause before executing.

---

## Part 4: Research Log

The research log provides a simple way to document observations, meeting notes, and project activities. Entries are stored in `ipd2.research_log` and are independent of experiment data (i.e. deletions do not affect other tables within the database).

### Add a Log Entry
```python
from forgedb import ForgeDB

db = ForgeDB()

# Minimal entry (remarks required, defaults applied)
db.add_log(remarks='Observed cooperation spike in episode 7')

# Entry with select parameters (remarks, subject, log date/time, and tags)
db.add_log(
    remarks='Breakthrough! Cooperation emerged spontaneously after round 12 without any prior coordination. Both agents shifted from mixed strategies to sustained mutual cooperation for the remaining 38 rounds. This occurred with temperature=0.7 and reflection_type=standard. Need to replicate.',
    subject='Discovery',
    log_dttm='2026-02-18 09:45:00',
    tags=['cooperation', 'emergence', 'breakthrough', 'llama3', 'replicate']
)

# Full entry with all parameters
db.add_log(
    remarks='Initial baseline test completed successfully',
    username='dhart',
    subject='Experiment',
    log_dttm='2026-02-15',
    tags=['llama3', 'baseline', 'cooperation']
)

db.close()
```

**Parameters:**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `remarks` | Yes | — | Detailed notes |
| `username` | No | Current OS user | Researcher name |
| `subject` | No | `'General'` | Brief description |
| `log_dttm` | No | Current timestamp | Effective date/time |
| `tags` | No | `None` | Single tag or Array of tags, e.g. `['llama3', 'test']` |

---

### Query Log Entries
```python
# All entries
df = db.get_log()

# Filter by username
df = db.get_log(username='dhart')

# Filter by subject (wildcard %)
df = db.get_log(subject='%Experiment%')

# Search remarks
df = db.get_log(remarks='%cooperation%')

# Filter by single tag
df = db.get_log(tags='llama3')

# Filter by multiple tags (ALL tags must be present on the log entry)
df = db.get_log(tags=['llama3', 'cooperation'])

# Filter by date range
df = db.get_log(start_date='2026-02-01', end_date='2026-02-15')

# Filter by date range with specific time
df = db.get_log(start_date='2026-02-15 08:00:00', end_date='2026-02-15 17:00:00')

# Combine filters
df = db.get_log(username='dhart', tags='experiment', limit=10)
```

**Parameters (all optional, wildcard=%):**

| Parameter | Description |
|-----------|-------------|
| `username` | Filter by researcher |
| `subject` | Filter by subject |
| `remarks` | Search within remarks text |
| `tags` | Single tag or list of tags (matches ALL if list) |
| `start_date` | Filter on/after this date/time |
| `end_date` | Filter before this date/time |
| `limit` | Maximum rows to return |

---

### Delete Log Entries
```python
# Delete a single log entry using a log entry ID number
db.delete_log(5)

# Delete multiple log entries using a list of IDs
db.delete_log([1, 3, 5])

# Delete a range of log entries using a tuple of ID start and end values (inclusive)
db.delete_log((1, 10))  # Deletes IDs 1 through 10
```

**Note:** Use a tuple `(start, end)` for a range. Use a list `[1, 3, 5]` for specific non-contiguous IDs.

---

### Research Log Table Structure

**Table:** `ipd2.research_log`

| Column | Type | Description |
|--------|------|-------------|
| `log_id` | `SERIAL` | Primary key (auto-generated) |
| `create_dttm` | `TIMESTAMPTZ` | When the entry was created |
| `log_dttm` | `TIMESTAMPTZ` | Effective date (what the note refers to) |
| `username` | `VARCHAR(64)` | Researcher who created the entry |
| `subject` | `VARCHAR(256)` | Brief description/category |
| `remarks` | `TEXT` | Detailed notes |
| `tags` | `TEXT[]` | Array of tags for filtering |

---

## Quick Reference Card

```python
from forgedb import ForgeDB
import pandas as pd

db = ForgeDB()

# Built-in query methods (all return DataFrames)
db.get_raw_data()               # Metadata + raw JSON
db.get_results()                # Full detail (all columns)
db.get_summary()                # Experiment summary (agents pivoted)
db.get_episode_summary()        # Episode summary (agents pivoted)
db.get_rounds_summary()         # Round summary (agents side-by-side)
db.get_rounds_detail()          # Round detail (per agent row)

# Common filters (all methods accept these)
db.get_summary(username='dhart')
db.get_summary(filename='%ep50%')
db.get_summary(start_date='2026-01-25', end_date='2026-02-01')
db.get_summary(limit=10)

# Ad hoc SQL
rows = db.query("SELECT * FROM ipd2.experiment_summary_vw WHERE username = 'dhart'")
df = pd.DataFrame(rows)

# CLI import
# python forgedb.py --import results/
# python forgedb.py --import results/game.json --username dhart

# Research log methods
db.add_log(remarks='Note text', subject='Topic', tags=['tag1', 'tag2'])
db.get_log(username='dhart', tags='experiment')
db.delete_log(5)           # Single ID
db.delete_log([1, 3, 5])   # List of IDs
db.delete_log((1, 10))     # Range (inclusive)

db.close()
```

---

## Troubleshooting

### Problem: Connection Refused
**Symptom:** `psycopg.OperationalError: connection refused`

Verify you can reach the database server:
```bash
ping platinum
psql -h platinum -d forge -U $USER -c "SELECT 1"
```

### Problem: Permission Denied
**Symptom:** `permission denied for schema ipd2`

See the [Verify Database Access](#verify-database-access) section to create your role and grant schema access. If issues persist, contact the principal investigators: Dr. Douglas Hart (douglas.hart@regis.edu) or Dr. Kellen Sorauf (kellen.sorauf@regis.edu).

### Problem: Duplicate File Skipped
**Symptom:** `Duplicate file skipped: results/game.json`

This is expected behavior. The database enforces uniqueness on filename and timestamp to prevent duplicate imports. The file was already loaded. If the duplicate filename and timestamp are valid, then please rename the file and edit the JSON to adjust the timestamp to make it unique (i.e. add a -1 to the filename, update the timestamp to increment the microseconds [2026-01-26T17:26:59.60087**0** -> 2026-01-26T17:26:59.60087**1**]).

### Problem: Import Fails on Older JSON Files
**Symptom:** `KeyError` on missing fields

Older JSON files may have a different structure. Check `forgedb.log` for the specific missing field. You may need to use the `--username` flag if the file predates the username field (prior to January 27th, 2026).

---

## Contact
Principal investigators:
**Doug Hart**: douglas.hart@regis.edu  
**Kellen Sorauf**: kellen.sorauf@regis.edu

Database & ETL author during Spring 2026 semester:
**Emily Carpenter**: emily.carpenter@regis.edu  

**Database Server:** `platinum` — Database: `forge` — Schema: `ipd2`

---

## Resources

- **psycopg3 Documentation:** https://www.psycopg.org/psycopg3/

## Citation
```
Carpenter, E. D. (2026, January-May). ForgeDB: Data access & ETL pipeline for
    IPD-LLM-Agents [Unpublished practicum project]. Anderson College
    of Business and Computing, Regis University.
```

## Acknowledgments

Database schema, ETL pipeline, and documentation developed with assistance from Claude (Anthropic; models used include Sonnet 4.5 and Opus 4.6). All code and content reviewed, edited, and approved by the author.

---

## Changelog

### Version 1.1 (February 22, 2026)
- Added research log functionality (add_log, get_log, delete_log)
- Added ON DELETE CASCADE to all foreign keys
- Created ipd2.research_log table

### Version 1.0 (February 2026)
- Initial release with ETL pipeline and query methods