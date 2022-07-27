from datasette import hookimpl

def build_search_idioms_sql(args):
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
    wheres = []
    for param in args.keys():
        if param in idiom_list_parameters.keys():
            param_sql_id = idiom_list_parameters[param]
            # If url parameter is present there should be a value, but keep the check to be sure
            param_values = [f"'{v}'" for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_values_str = ','.join(param_values)
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = i.strategy_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value COLLATE NOCASE IN ({param_values_str})
                        )""")
        if param in sentence_list_parameters.keys():
            param_sql_id = sentence_list_parameters[param]
            param_values = [f"'{v}'" for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_values_str = ','.join(param_values)
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM sentence_data_all sda WHERE sda.sentence_id = s.sentence_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value COLLATE NOCASE IN ({param_values_str})
                        )""")
        if param in idiom_text_parameters.keys():
            param_sql_id = idiom_text_parameters[param]
            # Empty text inputs are always submitted, so have to be filtered out
            text_param = args.get(param) if args.get(param) != '' else None
            if text_param:
                text_param = text_param.strip()
                if text_param.startswith('"') and text_param.endswith('"'):
                    term = text_param.strip('"')
                    # A quoted string should be found in a value (not necessarily match the entire value):
                    wheres.append(
                        f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = i.strategy_id
                            AND sda.parameter_definition_id = '{param_sql_id}'
                            AND sda.parameter_value LIKE '%{term}%'
                            )""")
                # Do not handle quotes inside a text parameter: either quoted, or match multiple strings
                if not '"' in text_param:
                    text_terms = text_param.split(' ')
                    for term in text_terms:
                        wheres.append(
                        f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = i.strategy_id
                            AND sda.parameter_definition_id = '{param_sql_id}'
                            AND sda.parameter_value LIKE '%{term}%'
                            )""")

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
    # Table "strategy" refers to idioms, therefore table alias "i"
    count_query = f"""SELECT count(DISTINCT strategy_id) as cnt
        FROM strategy i
        JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
        WHERE {wheres_str};"""
    main_query = f"""SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
        strategy_id, strategy_name, strategy_description
    FROM strategy i
    JOIN sentence s ON s.sentence_strategy_id = i.strategy_id
    WHERE {wheres_str}
    GROUP BY strategy_id, strategy_name, strategy_description
    ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

    return with_clauses + count_query, with_clauses + main_query


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
        "build_search_idioms_sql": build_search_idioms_sql,
        "get_interlinear": get_interlinear,
    }
