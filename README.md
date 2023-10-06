# Database of Dutch Dialect Idioms

This repository contains a [Datasette](https://datasette.io/) app for serving the [Database of Dutch Dialect Idioms](https://dutchdialectidioms.uu.nl/). It preserves the data structures of the now-retired original project database, and includes the data in TSV format.

## Datasette

Installing and running Datasette.

### Prerequisites

- Python (v3.9+)
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

    python scripts/create-db.py

Alternatively, download [idioms.db](https://dutchdialectidioms.uu.nl/idioms.db) and place it in the root directory of the project.

### Running Datasette

    source .env/bin/activate
    datasette serve .

## License

The data are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
The source code is licensed under the [3-Clause BSD License](https://opensource.org/license/bsd-3-clause/).
See the `LICENSE` file for details.
