import shlex
import subprocess

from datasette.app import Datasette
import pytest


@pytest.fixture(scope="session")
def datasette():
    # TODO: convert to Python script
    # res = subprocess.call(shlex.split("bash scripts/create-db.sh"))
    # if res != 0:
    #     raise Exception("Database creation was not successful.")
    # else:
    datasette = Datasette(files=["./idioms.db"])
    return datasette
