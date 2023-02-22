from collections import defaultdict
import re

from datasette import hookimpl
from datasette.utils import sqlite3


# Based on escape_fts() from datasette.
# Modified to not escape boolean operators.
_escape_fts_re = re.compile(r'\s+|(".*?")')


def escape_fts(query):
    # If query has unbalanced ", add one at end
    if query.count('"') % 2:
        query += '"'
    parts = _escape_fts_re.split(query)
    parts = [p for p in parts if p and p != '""']
    unquoted_keywords = ['AND', 'OR', 'NOT', '*']
    return " ".join(
        f'"{part}"' if not part.startswith('"') and part not in unquoted_keywords else part for part in parts
    )


def dict_and_keyset(dictionary):
    return dictionary, set(dictionary.keys())


# Mappings between form submission GET parameters (= HTML name attribute),
# and parameter identifiers recorded in the database.
# GET parameters could be shortened to cut down on URL character length.

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
    'ManipulatedProperty': 'Property1',
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

selectlist_keys = {'Dialect'} | idiom_list_parameter_keys | sentence_list_parameter_keys
text_param_keys = idiom_text_parameter_keys | sentence_text_parameter_keys
text_main_keys = idiom_fts_columns_keys | sentence_fts_columns_keys
text_keys = text_param_keys | text_main_keys
idiom_keys = idiom_list_parameter_keys | idiom_text_parameter_keys | idiom_fts_columns_keys
sentence_keys = sentence_list_parameter_keys | sentence_text_parameter_keys | sentence_fts_columns_keys | {'SentenceID'}

# SQL query constants
dialect_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
 strategy_answerset_id, answerset_name, answerset_description
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
JOIN answerset a ON i.strategy_answerset_id = a.answerset_id
WHERE {}
GROUP BY answerset_name
ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

# Table "strategy" refers to idioms, therefore table alias "i"
idiom_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
 strategy_id, strategy_name, strategy_description, strategy_answerset_id
FROM strategy i
LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
WHERE {}
GROUP BY strategy_id, strategy_name, strategy_description
ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

sentence_main_query = """SELECT ROW_NUMBER() OVER (ORDER BY i.strategy_id, s.sentence_id ASC) AS row_num,
 sentence_id, original, gloss, translation, convert_gramm(grammaticality) AS grammaticality,
 strategy_id, strategy_name, strategy_answerset_id, sentence_answerset_id
FROM sentence s
JOIN strategy i ON s.sentence_strategy_id = i.strategy_id
WHERE {}
ORDER BY i.strategy_id, s.sentence_id ASC;"""

queries = {
    'dialect': dialect_main_query,
    'idiom': idiom_main_query,
    'sentence': sentence_main_query
}


def build_exists_clause(kind, alias, id, criterion, search_type='param'):
    """ Arguments:
    - kind: 'strategy', 'sentence', 'strategy_data', 'sentence_data'
    - alias: 'i', 's'
    - id: parameter_definition_id or fts column
    - criterion: ?-placeholder strings
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


def build_where_expressions(param, value):
    """ Converts a search parameter into a WHERE expression
    Takes the parameter name and its value as arguments.
    Value is a string for text input, a list of strings for select list input.
    Returns a list of WHERE-clause strings and a list of values corresponding to
    SQL parameters (placeholders)."""

    if param in selectlist_keys:
        where = build_selectlist_where(param, value)
        return [where], value

    if param in text_param_keys:
        text_param_value = escape_fts(value)
        where = build_fts_param_where(param)
        return [where], [text_param_value]

    if param in text_main_keys:
        search_string = escape_fts(value)
        where = build_fts_main_where(param)
        return [where], [search_string]

    if param == 'SentenceID':
        return ["sentence_id = ?"], [value]

    return [], []  # Fallback


def build_search_sql(criteria, result_type):
    """ args is a dict of search criteria.
    result_type: idiom, sentence, or dialect.
    """
    wheres = []  # A list of where-clause strings
    wheres_values = []  # A list of values to provide as argument for ?-style SQL parameters

    for param in criteria.keys():
        where, where_values = build_where_expressions(param, criteria[param])
        wheres.extend(where)
        wheres_values.extend(where_values)

    if not wheres:
        # Make a valid SQL query in case no WHERE criterion has been added
        wheres.append('1')

    wheres_str = '\n AND '.join(wheres)

    # Subsitute anonymous ?-parameters with named parameters (numbered :0 etc.)
    wheres_str_split = wheres_str.split('?')
    i = 0
    wheres_str_numbered = ''
    for s in wheres_str_split:
        wheres_str_numbered += s
        if i < len(wheres_str_split) - 1:
            wheres_str_numbered += f":{i}"
        i += 1
    query = queries[result_type].format(wheres_str_numbered)
    wheres_obj = dict([(str(i), value) for i, value in enumerate(wheres_values)])

    return query, wheres_obj


def filter_search_criteria(args):
    """ Filter empty GET parameter values.
    :param args: request.args MultiParams object
    :return: dictionary of param and searched value
    """
    search_criteria = {}
    for param in args.keys():
        criterion = None
        param_values = args.getlist(param)
        if param in text_keys or param == 'SentenceID':
            criterion = param_values[0].strip()
        if param in selectlist_keys:
            criterion = list(filter(None, param_values))
        if criterion:
            search_criteria[param] = criterion

    return search_criteria


def get_interlinear(interlinear_sentence):
    """ Gets the word representations of original and gloss from a sentence,
    and zips the word combinations together.
    Returns a list of (original, gloss) tuples."""
    words_original = interlinear_sentence['original'].split(' ')
    words_gloss = interlinear_sentence['gloss'].split(' ')
    interlinear = list(zip(words_original, words_gloss))

    return interlinear


def get_grammaticality_text(gramm):
    # Maps the sentence.grammaticality values to a textual representation
    return {
        'ok': 'Mostly acceptable',
        '?': 'Moderately acceptable',
        '%': 'Acceptability varies by speaker',
        '?*': 'Barely acceptable',
        '*': 'Mostly not acceptable',
        'Unknown': 'Unknown',
    }[gramm]


@hookimpl
def prepare_connection(conn):
    """ Register a custom SQL function to convert the grammaticality judgment text value.
    https://docs.python.org/3.8/library/sqlite3.html#sqlite3.Connection.create_function
    """
    conn.create_function(
        "convert_gramm", 1, get_grammaticality_text
    )


@hookimpl
def extra_template_vars(datasette, request):
    criteria = filter_search_criteria(request.args)

    async def execute_search_query(result_type):
        db = datasette.get_database()
        try:
            query, wheres_values = build_search_sql(criteria, result_type)
            results = await db.execute(query, wheres_values)
            result_count = len(results)
            return result_count, results, query, wheres_values, None
        except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
            return None, None, None, None, str(e)

    async def get_search_params_display():
        db = datasette.get_database()
        result = await db.execute('SELECT * FROM parameter_labels')
        parameter_display_labels_obj = {}
        for row in result:
            label = ': '.join(list(filter(None, [row['group_entity'], row['group_label'], row['question_statement']])))
            parameter_display_labels_obj[row['param_get']] = label
        display = defaultdict(dict)
        for param, values in criteria.items():
            label = parameter_display_labels_obj[param]
            value = ', '.join(values) if isinstance(values, list) else values
            display[label] = value
        return display

    return {
        "args": request.args,
        "execute_search_query": execute_search_query,
        "get_interlinear": get_interlinear,
        "get_search_params_display": get_search_params_display,
    }
