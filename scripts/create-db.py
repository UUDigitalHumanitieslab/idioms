import csv
import os
import pathlib
import sqlite3

APP_ROOT = pathlib.Path(__file__).parents[1].resolve()
DB_PATH = os.path.join(APP_ROOT, 'idioms.db')

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Deleted existing {DB_PATH}")

with open(os.path.join(APP_ROOT, 'data', 'conversion', 'sql-create-tables.sql'), 'r') as sql_create_tables, \
     open(os.path.join(APP_ROOT, 'data', 'conversion', 'sql-create-fts.sql'), 'r') as sql_create_fts:
    sql_create_tables = sql_create_tables.read()
    sql_create_fts = sql_create_fts.read()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create the table and main view structures
print("Creating SQLite database idioms.db and table structures")
cur.executescript(sql_create_tables)

# # Import the table data from CSV (Order of the tables matters given foreign keys)
print("Importing CSV data into SQLite database:")

tables = ['valueType', 'valueDefinition', 'parameterGroup', 'parameterQuestion', 'parameterDefinition', 'answerset',
          'answerset_data', 'strategy', 'strategy_data', 'sentence', 'sentence_data']

for table in tables:
    tablefile = os.path.join(APP_ROOT, 'data', 'csv', table + '.tsv')
    print(f" * Importing {tablefile}")
    with open(tablefile, 'rt', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        # param_placeholders = ','.join(['?'] * len(reader.fieldnames))
        columns = ','.join([f':{column}' for column in reader.fieldnames])
        sql = f'INSERT INTO {table} VALUES ({columns});'
        cur.executemany(sql, reader)

# CSV cannot encode NULL values, and there's no good way to convert empty strings
# to NULLs on import (cf. https://github.com/simonw/sqlite-utils/issues/488)
# Restore NULLs so we don't need NULLIF()
cur.execute('UPDATE sentence_data SET value_text = NULL WHERE value_text = ""')
cur.execute('UPDATE sentence_data SET value_definition_id = NULL WHERE value_definition_id = ""')
cur.execute('UPDATE strategy_data SET value_shorttext = NULL WHERE value_shorttext = ""')
cur.execute('UPDATE strategy_data SET value_text = NULL WHERE value_text = ""')
cur.execute('UPDATE strategy_data SET value_definition_id = NULL WHERE value_definition_id = ""')
cur.execute('UPDATE parameterQuestion SET question_label = NULL WHERE question_label = ""')
cur.execute('UPDATE parameterQuestion SET question_statement_label = NULL WHERE question_statement_label = ""')
cur.execute('UPDATE valueDefinition SET value_label = NULL WHERE value_label = ""')

# Create the FTS5 virtual tables
print("Creating FTS5 virtual tables")
cur.executescript(sql_create_fts)

print("Finished database creation.")
