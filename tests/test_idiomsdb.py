import pytest
from .fixtures import datasette


@pytest.mark.asyncio
async def test_frontpage_default_html(datasette):
    response = await datasette.client.get("/")
    assert "<title>Datasette: idioms</title>" in response.text
