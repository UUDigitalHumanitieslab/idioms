#!/bin/bash

cd data

rm -f idioms.db

# Create the table and main view structures
sqlite3 idioms.db < conversion/sql-create-tables.sql

# Import the table data from CSV
TABLES='valueType valueDefinition parameterGroup parameterQuestion parameterDefinition answerset answerset_data strategy strategy_data sentence sentence_data'
for table in $TABLES ; do sqlite3 idioms.db '.mode quote' '.separator "\t"' ".import --skip 1 csv/$table.tsv $table"; done

# Create the FTS5 virtual tables
sqlite3 idioms.db < conversion/sql-create-fts.sql
