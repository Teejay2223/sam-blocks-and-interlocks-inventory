"""
Simple migration script: copy data from SQLite `database.db` into a Postgres database.
Usage:
  - Set DATABASE_URL in environment, e.g.:
      $env:DATABASE_URL = "postgresql://samuser:pass@localhost:5432/sam_blocks"
  - Then run:
      python migrate_sqlite_to_postgres.py

Notes:
  - This script runs the Postgres schema from `schema_pg.sql` then copies tables.
  - It preserves integer primary keys when possible and resets sequences.
  - Use with care and test on a disposable DB first.
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB = os.path.join(BASE_DIR, 'database.db')
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print('Please set DATABASE_URL environment variable pointing to Postgres. Example:')
    print('postgresql://user:pass@localhost:5432/dbname')
    raise SystemExit(1)

# Connect
sconn = sqlite3.connect(SQLITE_DB)
sconn.row_factory = sqlite3.Row
pconn = psycopg2.connect(DATABASE_URL)
pcur = pconn.cursor()

# Apply schema
with open(os.path.join(BASE_DIR, 'schema_pg.sql'), 'r', encoding='utf-8') as f:
    schema = f.read()
print('Applying Postgres schema...')
# execute each statement
for stmt in [s.strip() for s in schema.split(';') if s.strip()]:
    try:
        pcur.execute(stmt)
    except Exception as e:
        print('Warning applying statement:', e)
pconn.commit()

# Table list to migrate (order matters for FK integrity)
tables = [
    'users','customers','products','raw_materials','finished_blocks',
    'orders','order_items','payments','sales','trips','notes','product_audit','breakages','audit'
]

for tbl in tables:
    print(f'Copying table {tbl}...')
    # get columns from sqlite
    try:
        cols_info = sconn.execute(f"PRAGMA table_info({tbl})").fetchall()
    except Exception:
        print(f'  Skipping {tbl}: does not exist in sqlite DB')
        continue
    cols = [c['name'] for c in cols_info]
    if not cols:
        continue
    select_sql = f"SELECT {', '.join(cols)} FROM {tbl}"
    rows = sconn.execute(select_sql).fetchall()
    if not rows:
        print('  no rows')
        continue
    # build INSERT statement with explicit columns (preserve id if present)
    col_list = ', '.join(cols)
    placeholders = ', '.join(['%s'] * len(cols))
    insert_sql = f"INSERT INTO {tbl} ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    count = 0
    for r in rows:
        vals = [r[c] for c in cols]
        try:
            pcur.execute(insert_sql, vals)
            count += 1
        except Exception as e:
            print(f'  skip row due to error: {e}')
    pconn.commit()
    print(f'  copied {count} rows')

# Reset sequences for serial primary keys (best-effort)
for tbl in tables:
    try:
        # set sequence for `id` column if present
        try:
            pcur.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 0))")
        except Exception:
            # not all tables have id serials; ignore errors per-table
            pass
    except Exception:
        pass
pconn.commit()

print('Migration complete.')
sconn.close()
pcur.close()
pconn.close()
