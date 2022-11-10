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
