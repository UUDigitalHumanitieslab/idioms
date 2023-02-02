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
async def test_search_idioms_parameters(idiomsdb):
    # Result type: Idioms; Search on Dialect + Idiom + Sentence properties
    response = await idiomsdb.client.get('/search/idioms?Dialect=Dendermonds&Dialect=Drents&Dialect=Gronings&Idiom=&Meaning=&GenStructure=&OpenAnimacy=Animate&OpenAnimacy=Inanimate&IdiomNotes=&SentenceID=&Original=&Gloss=&Translation=&Judgments=&Property1=DefiniteDeterminer')
    assert '2 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_1(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Idiom=&Meaning=&GenStructure=&IdiomNotes=&SentenceID=&Original=&Gloss=get.PTCP&Translation=&Judgments=')
    assert '2 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_2(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Idiom=&Meaning=&GenStructure=V+DO&IdiomNotes=&SentenceID=&Original=&Gloss=&Translation=&Judgments=')
    assert '3900 records found' in response.text


@pytest.mark.asyncio
async def test_search_idioms_fts_3(idiomsdb):
    response = await idiomsdb.client.get('/search/idioms?Idiom=&Meaning=&GenStructure="V+DO"&IdiomNotes=&SentenceID=&Original=&Gloss=&Translation=&Judgments=')
    assert '3764 records found' in response.text


@pytest.mark.asyncio
async def test_search_sentences_1(idiomsdb):
    response = await idiomsdb.client.get('/search/sentences?Idiom=&Meaning=&Voice=Passive&Voice=0&GenStructure=&IdiomNotes=&SentenceID=&Original=&Gloss=&Translation=intelligent&Judgments=')
    assert '1 records found' in response.text


@pytest.mark.asyncio
async def test_search_dialects_1(idiomsdb):
    response = await idiomsdb.client.get('/search/dialects?Idiom=&Meaning=&GenStructure=&IdiomNotes=&SentenceID=&Original=&Gloss=&Translation=&Judgments=&DeterminerManipulations=Passive&DeterminerManipulations=EventivePassive&DeterminerManipulations=Active')
    assert '10 records found' in response.text
