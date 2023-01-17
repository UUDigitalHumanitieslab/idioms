# Database of Dutch Dialect Idioms

This repository contains a [Datasette](https://datasette.io/) app for serving the [Database of Dutch Dialect Idioms](https://dutchdialectidioms.uu.nl/). It preserves the data structures of the now-retired original project database, and includes the data in TSV format.

## Datasette

Installing and running Datasette.

### Prerequisites

- Python (v3.8+)
- SQLite
- pip

Optional:
- virtualenv

### Project setup

Create and activate your virtual environment:

    virtualenv .env --prompt="(idiomsdb) "
    source .env/bin/activate

Install Datasette dependencies:

    pip install -r requirements.txt

Import the data into a SQLite database:

    bash scripts/create-db.sh

Alternatively, download [idioms.db](https://dutchdialectidioms.uu.nl/idioms.db) and place it in the root directory of the project.

### Running Datasette

    source .env/bin/activate
    datasette serve .
