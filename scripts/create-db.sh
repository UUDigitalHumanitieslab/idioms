#!/bin/bash

rm -f idioms.db

# Create the table and main view structures
echo "Creating SQLite database idioms.db and table structures"
sqlite3 idioms.db < data/conversion/sql-create-tables.sql

# Import the table data from CSV (Order of the tables matters given foreign keys)
echo "Importing CSV data into SQLite database "
TABLES='valueType valueDefinition parameterGroup parameterQuestion parameterDefinition answerset answerset_data strategy strategy_data sentence sentence_data'
for table in $TABLES ; \
    do echo "Importing data/csv/$table.tsv"; \
    sqlite3 idioms.db '.mode quote' '.separator "\t"' ".import --skip 1 data/csv/$table.tsv $table"; \
    done

# CSV cannot encode NULL values, and there's no good way to convert empty strings
# to NULLs on import (cf. https://github.com/simonw/sqlite-utils/issues/488)
# Restore NULLs so we don't need NULLIF()
sqlite3 idioms.db 'UPDATE sentence_data SET value_text = NULL WHERE value_text = ""'
sqlite3 idioms.db 'UPDATE sentence_data SET value_definition_id = NULL WHERE value_definition_id = ""'
sqlite3 idioms.db 'UPDATE strategy_data SET value_shorttext = NULL WHERE value_shorttext = ""'
sqlite3 idioms.db 'UPDATE strategy_data SET value_text = NULL WHERE value_text = ""'
sqlite3 idioms.db 'UPDATE strategy_data SET value_definition_id = NULL WHERE value_definition_id = ""'
sqlite3 idioms.db 'UPDATE parameterQuestion SET question_label = NULL WHERE question_label = ""'
sqlite3 idioms.db 'UPDATE parameterQuestion SET question_statement_label = NULL WHERE question_statement_label = ""'
sqlite3 idioms.db 'UPDATE valueDefinition SET value_label = NULL WHERE value_label = ""'

# Create the FTS5 virtual tables
echo "Creating FTS5 virtual tables"
sqlite3 idioms.db < data/conversion/sql-create-fts.sql

echo "Finished"
