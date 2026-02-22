import pandas as pd, os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# test_forgedb.py
from forgedb import ForgeDB

db = ForgeDB()

# Test Raw data query
df = db.get_raw_data(limit=10)
print("Raw data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Results query
df = db.get_results(limit=10)
print("Results data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Experiment Summary query
df = db.get_summary(limit=10)
print("Experiment Summary data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Episode Summary query
df = db.get_episode_summary(limit=10)
print("Episode Summary data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Rounds Summary query
df = db.get_rounds_summary(limit=10)
print("Rounds Summary data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Rounds Details query
df = db.get_rounds_detail(limit=10)
print("Rounds Details data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()


# Test with filter
df = db.get_results(username='techkgirl', limit=50)
print(f"\nFiltered by username: {len(df)} rows")
print(df.head())
print()

# Test custom SQL
sql = """
    SELECT DISTINCT timestamp, username, hostname, agent_host
    FROM ipd2.results_vw 
    WHERE username = 'techkgirl'
    ORDER BY timestamp
"""

print('Testing custom SQL statement')
rows = db.query(sql)
df = pd.DataFrame(rows)
print(df.to_string())

db.close()