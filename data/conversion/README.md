## Project setup

### Legacy database in MySQL via Docker

Restore the MySQL database using Docker.

`docker-compose up`

Remove security definer to allow importing:

`sed -i '/^\/\*\!50013/d' data/idioms.sql`

Import the idioms database to the MySQL database running in Docker:

`docker exec -i idiomsdb sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D idiomsdb' < data/idioms.sql`

### MySQL-to-SQLite

Prerequisites:

- Python v3.8+
- pip
- libmysqlclient-dev (for Debian-based OS)

Optional:
- venv or virtualenv

Activate your virtual env if applicable, e.g:

    virtualenv .env --prompt="(idioms) "
    source .env/bin/activate

Install the dependencies:

    pip install -r requirements.txt

First create the tables, indexes, and views in a new SQLite database:

    sqlite3 idioms.db < sql-create-tables.sql

Import only the relevant tables and columns from MySQL:

    while IFS=: read table sql; do db-to-sqlite mysql://root:idiomsdb@127.0.0.1:3307/idiomsdb idioms.db --sql="$sql" --output="$table"; echo "Imported $table"; done < sql-import-selected.txt

Create the FTS5 virtual tables:

    sqlite3 idioms.db < sql-create-fts.sql
