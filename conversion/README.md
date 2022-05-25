## MySQL via Docker

Restore the MySQL database using Docker.

`docker-compose up`

Remove security definer to allow importing:

`sed -i '/^\/\*\!50013/d' data/idioms.sql`

Import the idioms database to the MySQL database running in Docker:

`docker exec -i idiomsdb sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -D idiomsdb' < data/idioms.sql`

### Prerequisites

- Python v3.8+
- pip
- libmysqlclient-dev (for Debian-based OS)

Optional:
- venv or virtualenv

### Install dependencies

Activate your virtual env if applicable, e.g:
    virtualenv .env --prompt="(idioms) "
    source .env/bin/activate

Install dependencies for copying MySQL data to a SQLite database:

    pip install -r requirements.txt

### Convert to SQLite

    db-to-sqlite mysql://root:idiomsdb@127.0.0.1:3307/idiomsdb data/idioms.db --all

