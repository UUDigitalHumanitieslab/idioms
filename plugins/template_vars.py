from datasette import hookimpl

def build_search_idioms_sql(args):
    # Mapping between form submission values and identifiers recorded in the
    # database. Keys may be shortened to cut down on URL character length.
    list_parameters = {
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
    text_parameters = {
        'GenStructure': 'GenStructure1',
        'IdiomNotes': 'IdiomNotes1',
    }
    wheres = []
    for param in args.keys():
        if param in list_parameters.keys():
            param_sql_id = list_parameters[param]
            # If url parameter is present there should be a value, but keep the check to be sure
            param_values = [f"'{v}'" for v in args.getlist(param) if v != '']
            if len(param_values) > 0:
                param_values_str = ','.join(param_values)
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = s.strategy_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value IN ({param_values_str})
                        )""")
        if param in text_parameters.keys():
            param_sql_id = text_parameters[param]
            # Empty text inputs are always submitted, so have to be filtered out
            text_param = args.get(param) if args.get(param) != '' else None
            # TODO: handle: 1. Multiple values separately; 2. Quoted string,
            # 3. AND, OR; 4. NULL / No Value.
            if text_param:
                wheres.append(
                    f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = s.strategy_id
                        AND sda.parameter_definition_id = '{param_sql_id}'
                        AND sda.parameter_value LIKE '%{text_param}%'
                        )""")

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
        )
        """
    count_query = f"SELECT count(*) as cnt FROM strategy s WHERE {wheres_str}"
    main_query = f"""SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num,
        strategy_id, strategy_name, strategy_description
    FROM strategy s
    WHERE {wheres_str}
    ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

    return with_clauses + count_query, with_clauses + main_query

@hookimpl
def extra_template_vars(request):
    return {
        "args": request.args,
        "build_search_idioms_sql": build_search_idioms_sql,
    }
