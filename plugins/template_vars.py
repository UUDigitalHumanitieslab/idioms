from datasette import hookimpl

def build_search_idioms_sql(args):
    wheres = []
    for param in args.keys():
        if param == 'Voice':
            param_values = [f"'{v}'" for v in args.getlist(param) if v != 'NULL']
            param_values_str = ','.join(param_values)
            wheres.append(
                f"""EXISTS (SELECT 1 FROM strategy_data sd WHERE sd.strategy = s.strategy_id
                 AND sd.parameter_definition_id = 'Voice1'
                 AND sd.value_definition_id IN ({param_values_str})
                 )""")
        if param == 'Tense':
            param_values = [f"'{v}'" for v in args.getlist(param) if v != 'NULL']
            param_values_str = ','.join(param_values)
            wheres.append(f"""EXISTS (SELECT 1 FROM strategy_data sd WHERE sd.strategy = s.strategy_id
            AND sd.parameter_definition_id = 'Tense1'
            AND sd.value_definition_id IN ({param_values_str}))""")

    wheres_str = '\n AND '.join(wheres)

    query = f"""SELECT ROW_NUMBER() OVER (ORDER BY strategy_answerset_id ASC, strategy_name ASC) AS row_num, strategy_name, strategy_description
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
