import pytest

from .fixtures import idiomsdb


@pytest.mark.asyncio
async def test_frontpage_default_html(idiomsdb):
    response = await idiomsdb.client.get('/')
    assert "<title>Database of Dutch Dialect Idioms (DaDDI)</title>" in response.text


@pytest.mark.asyncio
async def test_browse_dialects(idiomsdb):
    response = await idiomsdb.client.get('/dialects')
    assert '<a href="dialects/Aalsters">Aalsters</a>' in response.text


@pytest.mark.asyncio
async def test_dialect_idioms(idiomsdb):
    response = await idiomsdb.client.get('/dialects/Brugs')
    assert '1922 records found' in response.text
    assert '<a href="/idioms/3269">(Er) (zich) door boeren</a>' in response.text


@pytest.mark.asyncio
async def test_dialect_sentences(idiomsdb):
    response = await idiomsdb.client.get('/dialects/Brugs?page=sentences')
    assert '276 records found' in response.text


@pytest.mark.asyncio
async def test_idiom_sentences(idiomsdb):
    response = await idiomsdb.client.get('/idioms/78')
    # Presence of manipulated sentences for the idiom
    for i in range(570, 578):
        assert f'href="/sentences/{i}"' in response.text


@pytest.mark.asyncio
async def test_search_idioms_parameters(idiomsdb):
    # Result type: Idioms; Search on Dialect + Idiom + Sentence properties
    response = await idiomsdb.client.get('/search/idioms?Dialect=Dendermonds&Dialect=Drents&Dialect=Gronings&GenStructure=&OpenAnimacy=Animate&OpenAnimacy=Inanimate&ManipulatedProperty=DefiniteDeterminer')
    assert '2 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_1(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Gloss=get.PTCP')
    assert '2 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_2(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?GenStructure=V+DO')
    assert '3900 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_3(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?GenStructure="V+DO"')
    assert '3764 records found' in response.text


@pytest.mark.asyncio
async def test_search_sentences_1(idiomsdb):
    response = await idiomsdb.client.get('/search/sentences?Voice=Passive&Voice=0&Translation=intelligent')
    assert '1 records found' in response.text


@pytest.mark.asyncio
async def test_search_dialects_1(idiomsdb):
    response = await idiomsdb.client.get('/search/dialects?&DeterminerManipulations=Passive&DeterminerManipulations=EventivePassive&DeterminerManipulations=Active')
    assert '10 records found' in response.text


@pytest.mark.asyncio
async def test_search_fts_nulls(idiomsdb):
    response = await idiomsdb.client.get('/search/sentences?Translation=NULL')
    assert '1944 records found' in response.text


@pytest.mark.asyncio
async def test_search_fts_prefix_token(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Meaning=gevolg+*')
    assert '8 records found' in response.text


@pytest.mark.asyncio
async def test_search_fts_boolean_operators(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Idiom=ergens+AND+zijn')
    assert '10 records found' in response.text
    response = await idiomsdb.client.get('/search/sentences?Translation=NULL+OR+have')
    assert '2016 records found' in response.text
    response = await idiomsdb.client.get('/search/idioms?Idiom=hebben+NOT+in')
    assert '369 records found' in response.text
