from datasette import hookimpl

def build_search_idioms_sql(args):
    wheres = []
    for param in args.keys():
        if param == 'Voice':
            param_values = [f"'{v}'" for v in args.getlist(param) if v != 'NULL']
            param_values_str = ','.join(param_values)
            wheres.append(
                f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = s.strategy_id
                 AND sda.parameter_definition_id = 'Voice1'
                 AND sda.parameter_value IN ({param_values_str})
                 )""")
        if param == 'Tense':
            param_values = [f"'{v}'" for v in args.getlist(param) if v != 'NULL']
            param_values_str = ','.join(param_values)
            wheres.append(f"""EXISTS (SELECT 1 FROM strategy_data_all sda WHERE sda.strategy_id = s.strategy_id
             AND sda.parameter_definition_id = 'Tense1'
             AND sda.parameter_value IN ({param_values_str}))""")

    wheres_str = '\n AND '.join(wheres)

    query = f"""WITH strategy_parameter_ids AS (
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
        SELECT spc.strategy_id, spc.parameter_definition_id, IFNULL(COALESCE(sd.value_shorttext, sd.value_text, sd.value_definition_id), 0) AS parameter_value
        FROM strategy_parameter_combinations spc
        LEFT JOIN strategy_data sd
            ON sd.parameter_definition_id = spc.parameter_definition_id
             AND sd.strategy = spc.strategy_id
        )
    SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num, strategy_name, strategy_description
    FROM strategy s
    WHERE {wheres_str}
    ORDER BY strategy_answerset_id ASC, strategy_name ASC;"""

    return query

@hookimpl
def extra_template_vars(request):
    return {
        "args": request.args,
        "build_search_idioms_sql": build_search_idioms_sql,
    }
