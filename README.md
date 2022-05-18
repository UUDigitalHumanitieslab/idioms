# Database of Dutch Dialect Idioms

This repository documents the conversion of the [idioms database](https://idioms.hum.uu.nl/) from a PHP/MySQL app to a read-only SQLite-based app.

## Docker

`docker-compose up`

Remove security definer to allow importing:

`sed -i '/^\/\*\!50013/d' data/idioms.sql`

Import the idioms database to the MySQL database running in Docker:

`docker exec -i idiomsdb sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D idiomsdb' < data/idioms.sql`

## Datasette

Installation, assuming a Debian-based OS.

### Prerequisites

- Python v3.8+
- pip, pip-tools
- virtualenv
- libmysqlclient-dev

### Virtual environment

    virtualenv .env --prompt="(idioms) "
    source .env/bin/activate
    pip install -r requirements.txt

### Convert to SQLite

db-to-sqlite mysql://root:idiomsdb@127.0.0.1:3307/idiomsdb data/idioms.db --all

### Run Datasette

datasette data/idioms.db --metadata metadata.json --template-dir=templates/ --static static:static/ --plugins-dir=plugins/
