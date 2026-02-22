#!/usr/bin/env python3
import os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

from forgedb import ForgeDB

db = ForgeDB()

reset_log = False

# Reset research_log table (truncate and reset identity)
if reset_log:
    with db.conn.cursor() as cur:
        cur.execute("TRUNCATE ipd2.research_log RESTART IDENTITY")
    db.conn.commit()
    print("Research log reset")

# Test add_log with 10 entries
entries = [
    {'remarks': 'Initial baseline test with llama3 model', 'subject': 'Experiment', 'tags': ['llama3', 'baseline', 'script_test']},
    {'remarks': 'Observed high cooperation rates in episode 5', 'subject': 'Observation', 'tags': ['cooperation', 'episode5', 'script_test']},
    {'remarks': 'Server timeout issues on iron node', 'subject': 'Technical', 'tags': ['iron', 'timeout', 'bug', 'script_test']},
    {'remarks': 'Meeting with Dr. Hart about experiment parameters', 'subject': 'Meeting', 'tags': ['meeting', 'parameters', 'script_test']},
    {'remarks': 'Defection spike when temperature increased to 0.9', 'subject': 'Observation', 'tags': ['defection', 'temperature', 'script_test']},
    {'remarks': 'Imported 20 new game sessions from dhart', 'subject': 'Data Import', 'tags': ['import', 'dhart', 'script_test']},
    {'remarks': 'Testing reflection type variations', 'subject': 'Experiment', 'tags': ['reflection', 'test', 'script_test']},
    {'remarks': 'Database backup completed successfully', 'subject': 'Maintenance', 'tags': ['backup', 'database', 'script_test']},
    {'remarks': 'Cooperation emerged after round 15 consistently', 'subject': 'Observation', 'tags': ['cooperation', 'emergence', 'script_test']},
    {'remarks': 'Need to investigate agent_1 reasoning patterns', 'subject': 'TODO', 'tags': ['agent_1', 'reasoning', 'investigate', 'script_test']},
]

for entry in entries:
    log_id = db.add_log(
        remarks=entry['remarks'],
        subject=entry['subject'],
        tags=entry['tags']
    )

# Test get_log - all entries
print("\n--- All entries ---")
df = db.get_log()
print(df)

# Test get_log with tag filter
print("\n--- Filtered by tag 'cooperation' ---")
df = db.get_log(tags='cooperation')
print(df)

# Test get_log with multiple tags
print("\n--- Filtered by tags ['cooperation', 'emergence'] ---")
df = db.get_log(tags=['cooperation', 'emergence'])
print(df)

# Test get_log with subject filter
print("\n--- Filtered by subject 'Observation' ---")
df = db.get_log(subject='Observation')
print(df)

# Test delete_log
deleted = db.delete_log(log_id)
print(f"\nDeleted: {deleted}")

# Test get_log - all entries
print("\n--- All entries After Delete ---")
df = db.get_log()
print(df)

db.close()
print("\n--- Done ---")