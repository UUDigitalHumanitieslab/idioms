/*
 * Create FTS5 index for "strategy" text parameters
 */
CREATE VIRTUAL TABLE "strategy_fts" USING FTS5 (
    strategy_id
    , strategy_name
    , strategy_description
    , tokenize="unicode61"
);

INSERT INTO "strategy_fts" (strategy_id, strategy_name, strategy_description)
SELECT strategy_id, strategy_name, strategy_description
FROM strategy;

/*
 * Create FTS5 index for "sentence" text parameters
 */
CREATE VIRTUAL TABLE "sentence_fts" USING FTS5 (
    sentence_id
    , original
    , gloss
    , "translation"
    , tokenize="unicode61"
);

INSERT INTO "sentence_fts" (sentence_id, original, gloss, "translation")
SELECT sentence_id, original, gloss, "translation"
FROM sentence;

/*
 * Create FTS5 index for "strategy_data" text parameters
 */
CREATE VIRTUAL TABLE "strategy_data_fts" USING FTS5 (
    strategy_id
    , parameter_definition_id
    , parameter_value
    , tokenize="unicode61"
);

-- The views strategy_data_all/sentence_data_all use "0" for NULL values to simplify queries.
-- Use the string 'NULL' instead for use in FTS queries.
INSERT INTO "strategy_data_fts" (strategy_id, parameter_definition_id, parameter_value)
SELECT strategy_id, parameter_definition_id, replace(parameter_value, '0', 'NULL')
FROM strategy_data_all
WHERE parameter_definition_id IN ('GenStructure1', 'IdiomNotes1');

/*
 * Create FTS5 index for sentence_data text parameters
 */
CREATE VIRTUAL TABLE "sentence_data_fts" USING FTS5 (
    sentence_id
    , parameter_definition_id
    , parameter_value
    , tokenize="unicode61"
);

INSERT INTO "sentence_data_fts" (sentence_id, parameter_definition_id, parameter_value)
SELECT sentence_id, parameter_definition_id, replace(parameter_value, '0', 'NULL')
FROM sentence_data_all
WHERE parameter_definition_id IN ('s:judgments1');
