import pandas as pd

# test_forgedb.py
from forgedb import ForgeDB

db = ForgeDB()

# Test Results query
df = db.get_results(limit=10)
print("Results data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Summary query
df = db.get_summary(limit=10)
print("Summary data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()

# Test Rounds query
df = db.get_rounds(limit=10)
print("Summary data")
print(f"Rows returned: {len(df)}")
print(df.head())
print()


# Test with filter
df = db.get_results(username='techkgirl', limit=50)
print(f"\nFiltered by username: {len(df)} rows")
print(df.head())

sql = """
    SELECT DISTINCT timestamp, username, agent_host
    FROM ipd2.results_vw 
    --WHERE username = 'dhart'
    ORDER BY timestamp
"""

rows = db.query(sql)
df = pd.DataFrame(rows)
print(df.to_string())

db.close()