import os
import pathlib
import pytest

from datasette.app import Datasette


APP_ROOT = pathlib.Path(__file__).parents[1].resolve()


@pytest.fixture(scope="session")
def idiomsdb():
    settings = {
        "num_sql_threads": 1,
    }
    ds = Datasette(
        files=[os.path.join(APP_ROOT, 'idioms.db')],
        immutables=[],
        plugins_dir='plugins',
        settings=settings,
        inspect_data='inspect-data.json',
        static_mounts=[("static", os.path.join(APP_ROOT, 'static'))],
        template_dir='templates',
    )
    return ds
