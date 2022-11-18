import re

from datasette import hookimpl
from datasette.app import Datasette
from datasette.utils import sqlite3
from datasette.views.base import DatasetteError

from pyparsing import *

try:
    datasette = Datasette(files=["./idioms.db"])
    db = datasette.get_database('idioms')
except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
    raise DatasetteError(str(e), title="SQL Error", status=400)


# Based on escape_fts() from datasette.
# Modified to not escape boolean operators.
_escape_fts_re = re.compile(r'\s+|(".*?")')

def escape_fts(query):
    # If query has unbalanced ", add one at end
    if query.count('"') % 2:
        query += '"'
    parts = _escape_fts_re.split(query)
    parts = [p for p in parts if p and p != '""']
    return " ".join(
        f'"{part}"' if not part.startswith('"') and not part in ['AND', 'OR', 'NOT'] else part for part in parts
    )


def dict_and_keyset(dictionary):
    return dictionary, set(dictionary.keys())

# Mappings between form submission parameters (name attribute),
# and parameter identifiers recorded in the database.
# Keys may be shortened to cut down on URL character length.

idiom_list_parameters, idiom_list_parameter_keys = dict_and_keyset({
    'Voice': 'Voice1',
    'Tense': 'Tense1',
    'Aspect': 'Aspect1',
    'Modality': 'Modality1',
    'OpenPosition': 'OpenPosition1',
    'OpenAnimacy': 'OpenAnimacy1',
    'SpecialVerb': 'SpecialVerb1',
    'DODeterminer': 'DODeterminer1',
    'Modifier': 'Modifier1',
    'PossType': 'PossType1',
    'Alienability': 'Alienability1',
})

sentence_list_parameters, sentence_list_parameter_keys = dict_and_keyset({
    'Property1': 'Property1',
    'DeterminerManipulations': 'DeterminerManipulations1',
    'ModalityManipulations': 'ModalityManipulations1',
    'PossessiveManipulations': 'PossessiveManipulations1',
    'ExternalPossessionManipulation': 'ExternalPossessionManipulation',
    'FutureWordenManipulations': 'FutureWordenManipulations1',
    'TenseVoiceAspectManipulations': 'TenseVoiceAspectManipulations1',
})

idiom_text_parameters, idiom_text_parameter_keys = dict_and_keyset({
    'GenStructure': 'GenStructure1',
    'IdiomNotes': 'IdiomNotes1',
})

sentence_text_parameters, sentence_text_parameter_keys = dict_and_keyset({
    'Judgments': 's:judgments1',
})

idiom_fts_columns, idiom_fts_columns_keys = dict_and_keyset({
    'Idiom': 'strategy_name',
    'Meaning': 'strategy_description',
})

sentence_fts_columns, sentence_fts_columns_keys = dict_and_keyset({
    'Original': 'original',
    'Gloss': 'gloss',
    'Translation': 'translation',
})


selectlist_keys = set('Dialect') | idiom_list_parameter_keys | sentence_list_parameter_keys
textparam_keys = idiom_text_parameter_keys | sentence_text_parameter_keys
text_fts_keys = idiom_fts_columns_keys | sentence_fts_columns_keys


# SQL query constants
dialect_count_query = """SELECT count(DISTINCT strategy_answerset_id) as cnt
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
JOIN answerset a ON i.strategy_answerset_id = a.answerset_id
WHERE {};"""

dialect_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
 strategy_answerset_id, answerset_name, answerset_description
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
JOIN answerset a ON i.strategy_answerset_id = a.answerset_id
WHERE {}
GROUP BY answerset_name
ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

# Table "strategy" refers to idioms, therefore table alias "i"
idiom_count_query = """SELECT count(DISTINCT strategy_id) as cnt
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
WHERE {};"""

idiom_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
 strategy_id, strategy_name, strategy_description, strategy_answerset_id
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
WHERE {}
GROUP BY strategy_id, strategy_name, strategy_description
ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

sentence_count_query = """SELECT count(DISTINCT sentence_id) as cnt
FROM sentence s
JOIN strategy i ON s.sentence_strategy_id = i.strategy_id
WHERE {};"""

sentence_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY sentence_id ASC) AS row_num,
 sentence_id, original, gloss, translation, grammaticality,
 strategy_id, strategy_name, strategy_answerset_id, sentence_answerset_id
FROM sentence s
JOIN strategy i ON s.sentence_strategy_id = i.strategy_id
WHERE {}
ORDER BY i.strategy_id ASC;"""

queries = {
    'dialect': {
        'main_query': dialect_main_query
    },
    'idiom': {
        'main_query': idiom_main_query
    },
    'sentence': {
        'main_query': sentence_main_query
    }
}


def parse_search_string(user_search_text):
    quoted_string.setParseAction(removeQuotes)
    word = Word(srange("[a-zA-Z0-9_]"), srange("[a-zA-Z0-9_]"))
    phrases_pattern = ZeroOrMore(quoted_string) + ZeroOrMore(word)
    phrases = phrases_pattern.parse_string(user_search_text).asList()
    return phrases


def build_exists_clause(kind, alias, id, criterion, search_type='param'):
    """ Arguments:
    - kind: 'strategy', 'sentence', 'strategy_data', 'sentence_data'
    - alias: 'i', 's'
    - id: parameter_definition_id or fts column
    - criterion: string
    Returns a formatted EXISTS clause as a string.
    """
    if search_type == 'fts_main':
        return f"""{kind}_id IN (
            SELECT {kind}_id FROM {kind}_fts
            WHERE {kind}_fts.{id} {criterion}
        )"""
    if search_type == 'fts_param':
        table = kind + '_data_fts'
        return f"""{kind}_id IN (
            SELECT {kind}_id FROM {table}
            WHERE {table}.parameter_definition_id = '{id}'
             AND {table}.parameter_value {criterion}
        )"""
    else:
        return f"""EXISTS (
        SELECT 1 FROM {kind}_data_all sda
        WHERE sda.{kind}_id = {alias}.{kind}_id
         AND sda.parameter_definition_id = '{id}'
         AND sda.parameter_value {criterion}
        )"""


def build_selectlist_where(param, param_values):
    param_placeholders = ','.join(['?'] * len(param_values))
    criterion = f"COLLATE NOCASE IN ({param_placeholders})"
    if param == 'Dialect':
        return f"strategy_answerset_id IN ({param_placeholders})"
    if param in idiom_list_parameter_keys:
        return build_exists_clause('strategy', 'i', idiom_list_parameters[param], criterion)
    if param in sentence_list_parameter_keys:
        return build_exists_clause('sentence', 's', sentence_list_parameters[param], criterion)


def build_fts_param_where(param):
    # Search FTS5 index on text parameters from strategy_data/sentence_data tables
    criterion = "MATCH ?"
    if param in idiom_text_parameter_keys:
        return build_exists_clause('strategy', 'i', idiom_text_parameters[param], criterion, search_type='fts_param')
    if param in sentence_text_parameter_keys:
        return build_exists_clause('sentence', 's', sentence_text_parameters[param], criterion, search_type='fts_param')


def build_fts_main_where(param):
    # Search FTS5 index from main strategy/sentence tables
    criterion = "MATCH ?"
    if param in idiom_fts_columns_keys:
        return build_exists_clause('strategy', 'i', idiom_fts_columns[param], criterion, search_type='fts_main')
    if param in sentence_fts_columns_keys:
        return build_exists_clause('sentence', 's', sentence_fts_columns[param], criterion, search_type='fts_main')


def build_where_clauses(param, arg):
    """ Converts a single search parameter into one or more WHERE-clause strings.
    Takes the parameter name and its text value as arguments.
    Returns a list of WHERE-clause strings and a list of values corresponding to ?-style
    parameter placeholders."""

    if param in selectlist_keys:
        values = list(filter(None, arg))
        if len(values) > 0:
            where = build_selectlist_where(param, values)
            return [where], values

    if param in textparam_keys:
        arg = arg[0] # For text inputs there is just one value
        text_param_value = arg.strip() # Empty text input fields are always submitted
        if text_param_value:
            text_param_value = escape_fts(text_param_value)
            where = build_fts_param_where(param)
            return [where], [text_param_value]

    if param in text_fts_keys:
        arg = arg[0]
        search_string = arg.strip()
        if search_string:
            search_string = escape_fts(search_string)
            where = build_fts_main_where(param)
            return [where], [search_string]


    if param == 'SentenceID':
        arg = arg[0]
        int_param = arg if arg != '' and arg.isdigit else None
        if int_param:
            return ["sentence_id = ?"], [int_param]

    return [], [] # Fallback


def build_search_sql(args, result_type):
    """ args is the request.args MultiParams object.
    result_type: idiom, sentence, or dialect.
    """
    wheres = [] # A list of where-clause strings
    wheres_values = [] # A list of values to provide as argument for ?-style SQL parameters

    for param in args.keys():
        arg = args.getlist(param)
        where, where_values = build_where_clauses(param, arg)
        wheres.extend(where)
        wheres_values.extend(where_values)

    if not wheres:
        # Make a valid SQL query in case no WHERE criterion has been added
        wheres.append('1')

    wheres_str = '\n AND '.join(wheres)

    query = queries[result_type]['main_query'].format(wheres_str)

    return query, wheres_values


async def execute_search_query(args, result_type):
    try:
        query, wheres_values = build_search_sql(args, result_type)
        results =  await db.execute(query, wheres_values)
        result_count = len(results)
        return result_count, results, query, wheres_values
    except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
        raise DatasetteError(str(e), title="SQL Error", status=400)


def get_interlinear(interlinear_sentence):
    """ Gets the word representations of original and gloss from a sentence,
    and zips the word combinations together.
    Returns a list of (original, gloss) tuples."""
    words_original = interlinear_sentence['original'].split(' ')
    words_gloss = interlinear_sentence['gloss'].split(' ')
    interlinear = list(zip(words_original, words_gloss))

    return interlinear


@hookimpl
def extra_template_vars(request):
    return {
        "args": request.args,
        "execute_search_query": execute_search_query,
        "get_interlinear": get_interlinear,
    }
