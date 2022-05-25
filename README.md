# Database of Dutch Dialect Idioms

This repository contains a customized Datasette app that serves the data from the [idioms database](https://idioms.hum.uu.nl/) via a read-only SQLite database, preserving the original data structures. The steps for converting the data from the original MySQL database are listed in the "conversion" directory.

## Datasette

Installing and running Datasette.
### Prerequisites

- Python (v3.8+)
- SQLite
- pip

Optional:
- venv or virtualenv

### Install dependencies

Activate your virtual env if applicable, e.g:
    virtualenv .env --prompt="(idioms) "
    source .env/bin/activate

Install Datasette dependencies:

    pip install -r requirements.txt

### Run Datasette

    datasette data/idioms.db --metadata metadata.json --template-dir=templates/ --static static:static/ --plugins-dir=plugins/
