CREATE VIRTUAL TABLE "strategy_fts" USING FTS5 (
    strategy_id
    , strategy_name
    , strategy_description
    , tokenize="trigram"
);

INSERT INTO "strategy_fts" (strategy_id, strategy_name, strategy_description)
SELECT strategy_id, strategy_name, strategy_description
FROM strategy;

CREATE VIRTUAL TABLE "sentence_fts" USING FTS5 (
    sentence_id
    , original
    , gloss
    , "translation"
    , tokenize="trigram"
);

INSERT INTO "sentence_fts" (sentence_id, original, gloss, "translation")
SELECT sentence_id, original, gloss, "translation"
FROM sentence;

/*
 * Create FTS5 index for strategy_data text parameters
 */
CREATE VIRTUAL TABLE "strategy_data_fts" USING FTS5 (
    strategy_id
    , parameter_definition_id
    , parameter_value
    , tokenize="trigram"
);

WITH strategy_parameter_ids AS (
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
    -- Use string 'NULL' for NULL values to allow using it in FTS queries on text parameters
    SELECT spc.strategy_id, spc.parameter_definition_id,
        IFNULL(COALESCE(sd.value_shorttext, sd.value_text, sd.value_definition_id), 'NULL') AS parameter_value
    FROM strategy_parameter_combinations spc
    LEFT JOIN strategy_data sd
        ON sd.parameter_definition_id = spc.parameter_definition_id
            AND sd.strategy = spc.strategy_id
    ),
strategy_data_all_fts AS (
    SELECT strategy_id, parameter_definition_id, parameter_value
    FROM strategy_data_all
    WHERE parameter_definition_id IN ('GenStructure1', 'IdiomNotes1')
    )
INSERT INTO "strategy_data_fts" (strategy_id, parameter_definition_id, parameter_value)
SELECT strategy_id, parameter_definition_id, parameter_value
FROM strategy_data_all_fts;

/*
 * Create FTS5 index for sentence_data text parameters
 */
CREATE VIRTUAL TABLE "sentence_data_fts" USING FTS5 (
    sentence_id
    , parameter_definition_id
    , parameter_value
    , tokenize="trigram"
);

WITH sentence_parameter_ids AS (
    SELECT DISTINCT sd.parameter_definition_id
    FROM sentence_data sd
    ),
sentence_parameter_combinations AS (
    SELECT s.sentence_id, sp.parameter_definition_id, s.original, s."translation", s.gloss
    FROM sentence s
    CROSS JOIN sentence_parameter_ids sp
    ),
sentence_data_all AS (
    SELECT spc.sentence_id, spc.parameter_definition_id,
        IFNULL(COALESCE(sd.value_text, sd.value_definition_id), 'NULL') AS parameter_value,
        spc.original
    FROM sentence_parameter_combinations spc
    LEFT JOIN sentence_data sd
        ON sd.parameter_definition_id = spc.parameter_definition_id
            AND sd.sentence = spc.sentence_id
    ),
sentence_data_all_fts AS (
    SELECT sentence_id, parameter_definition_id, parameter_value
    FROM sentence_data_all
    WHERE parameter_definition_id IN ('s:judgments1')
    )
INSERT INTO "sentence_data_fts" (sentence_id, parameter_definition_id, parameter_value)
SELECT sentence_id, parameter_definition_id, parameter_value
FROM sentence_data_all_fts;
