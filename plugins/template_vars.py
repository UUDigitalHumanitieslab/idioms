from datasette import hookimpl
from pyparsing import *


# Mapping between form submission parameters (name attribute),
# and parameter identifiers recorded in the database.
# Keys may be shortened to cut down on URL character length.
idiom_list_parameters = {
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
}

sentence_list_parameters = {
    'Property1': 'Property1',
    'DeterminerManipulations': 'DeterminerManipulations1',
    'ModalityManipulations': 'ModalityManipulations1',
    'PossessiveManipulations': 'PossessiveManipulations1',
    'ExternalPossessionManipulation': 'ExternalPossessionManipulation',
    'FutureWordenManipulations': 'FutureWordenManipulations1',
    'TenseVoiceAspectManipulations': 'TenseVoiceAspectManipulations1',
}

idiom_text_parameters = {
    'GenStructure': 'GenStructure1',
    'IdiomNotes': 'IdiomNotes1',
}


def parse_search_string(user_search_text):
    quoted_string.setParseAction(removeQuotes)
    word = Word(srange("[a-zA-Z0-9_]"), srange("[a-zA-Z0-9_]"))
    phrases_pattern = ZeroOrMore(quoted_string) + ZeroOrMore(word)
    phrases = phrases_pattern.parse_string(user_search_text).asList()
    return phrases


def build_search_sql(args, result_type):
    """ args is the request.args MultiParams object.
    result_type: idiom, sentence, or dialect.
    """
    wheres = [] # A list of where-clause strings
    wheres_values = [] # A list of values to provide as argument for ?-style SQL parameters
    # ?-style parameters make it harder to debug long queries;
    # consider generating numbered parameters for use as :topic-style named parameters.
    for param in args.keys():
        if param == 'Dialect':
            param_values = [v for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_placeholders = ','.join(['?' for v in param_values])
                wheres.append(
                    # Filtering on strategy_answerset_id should suffice for both idioms and sentences
                    f"""strategy_answerset_id IN ({param_placeholders})""")
                wheres_values.extend(param_values)
        if param in idiom_list_parameters.keys():
            param_sql_id = idiom_list_parameters[param]
            # If url parameter is present there should be a value, but keep the check to be sure
            param_values = [v for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_placeholders = ','.join(['?' for v in param_values])
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = i.strategy_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value COLLATE NOCASE IN ({param_placeholders})
                        )""")
                wheres_values.extend(param_values)
        if param in sentence_list_parameters.keys():
            param_sql_id = sentence_list_parameters[param]
            param_values = [v for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_placeholders = ','.join(['?' for v in param_values])
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM sentence_data_all sda WHERE sda.sentence_id = s.sentence_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value COLLATE NOCASE IN ({param_placeholders})
                        )""")
                wheres_values.extend(param_values)
        if param in idiom_text_parameters.keys():
            param_sql_id = idiom_text_parameters[param]
            # Empty text inputs are always submitted, so have to be filtered out
            text_param = args.get(param).strip() if args.get(param) != '' else None
            if text_param:
                phrases = parse_search_string(text_param)
                for phrase in phrases:
                    wheres.append(
                    f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = i.strategy_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value LIKE '%' || ? || '%'
                        )""")
                    wheres_values.append(phrase)

    if not wheres:
        # Make a valid SQL query in case no WHERE criterion has been added
        wheres.append('1')

    wheres_str = '\n AND '.join(wheres)

    with_clauses = f"""WITH strategy_parameter_ids AS (
        SELECT DISTINCT sd.parameter_definition_id
        FROM strategy_data sd
        WHERE sd.parameter_definition_id != 'test10'
        ),
    strategy_parameter_combinations AS (
        SELECT strategy_id, parameter_definition_id
        FROM strategy s
        CROSS JOIN strategy_parameter_ids sp
        ),
    strategy_data_all AS (
        -- Note: value_shorttext, value_text, and value_definition_id values are mutually exclusive in the database
        SELECT spc.strategy_id, spc.parameter_definition_id,
            IFNULL(COALESCE(sd.value_shorttext, sd.value_text, sd.value_definition_id), '0') AS parameter_value
        FROM strategy_parameter_combinations spc
        LEFT JOIN strategy_data sd
            ON sd.parameter_definition_id = spc.parameter_definition_id
             AND sd.strategy = spc.strategy_id
        ),
    sentence_parameter_ids AS (
        SELECT DISTINCT sd.parameter_definition_id
        FROM sentence_data sd
        ),
    sentence_parameter_combinations AS (
        SELECT sentence_id, parameter_definition_id
        FROM sentence s
        CROSS JOIN sentence_parameter_ids sp
        ),
    sentence_data_all AS (
        -- Note: value_text and value_definition_id values are mutually exclusive in the database
        SELECT spc.sentence_id, spc.parameter_definition_id,
            IFNULL(COALESCE(sd.value_text, sd.value_definition_id), '0') AS parameter_value
        FROM sentence_parameter_combinations spc
        LEFT JOIN sentence_data sd
            ON sd.parameter_definition_id = spc.parameter_definition_id
             AND sd.sentence = spc.sentence_id
        )
        """

    if result_type == 'idiom':
        # Table "strategy" refers to idioms, therefore table alias "i"
        count_query = f"""SELECT count(DISTINCT strategy_id) as cnt
            FROM strategy i
            LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
            WHERE {wheres_str};"""
        main_query = f"""SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
            strategy_id, strategy_name, strategy_description, strategy_answerset_id
        FROM strategy i
        LEFT JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
        WHERE {wheres_str}
        GROUP BY strategy_id, strategy_name, strategy_description
        ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

    if result_type == 'sentence':
        count_query = f"""SELECT count(DISTINCT sentence_id) as cnt
            FROM sentence s
            JOIN strategy i ON s.sentence_strategy_id = i.strategy_id
            WHERE {wheres_str};"""
        main_query = f"""SELECT ROW_NUMBER() OVER (ORDER BY sentence_id ASC) AS row_num,
            sentence_id, original, gloss, translation, grammaticality,
            strategy_id, strategy_name, strategy_answerset_id, sentence_answerset_id
        FROM sentence s
        JOIN strategy i ON s.sentence_strategy_id = i.strategy_id
        WHERE {wheres_str}
        ORDER BY sentence_id ASC;"""

    return with_clauses + count_query, with_clauses + main_query, wheres_values


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
        "build_search_sql": build_search_sql,
        "get_interlinear": get_interlinear,
    }
