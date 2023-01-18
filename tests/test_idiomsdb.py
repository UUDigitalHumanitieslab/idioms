import pytest

from .fixtures import idiomsdb


@pytest.mark.asyncio
async def test_frontpage_default_html(idiomsdb):
    response = await idiomsdb.client.get("/")
    assert "<title>Database of Dutch Dialect Idioms (DaDDI)</title>" in response.text
