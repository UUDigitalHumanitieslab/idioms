#!/bin/bash

rm -f idioms.db

# Create the table and main view structures
echo "Creating SQLite database idioms.db and table structures"
sqlite3 idioms.db < data/conversion/sql-create-tables.sql

# Import the table data from CSV
echo "Importing CSV data into SQLite database "
TABLES='valueType valueDefinition parameterGroup parameterQuestion parameterDefinition answerset answerset_data strategy strategy_data sentence sentence_data'
for table in $TABLES ; \
    do echo "Importing data/csv/$table.tsv"; \
    sqlite3 idioms.db '.mode quote' '.separator "\t"' ".import --skip 1 data/csv/$table.tsv $table"; \
    done

# Create the FTS5 virtual tables
echo "Creating FTS5 virtual tables"
sqlite3 idioms.db < data/conversion/sql-create-fts.sql

echo "Finished"
