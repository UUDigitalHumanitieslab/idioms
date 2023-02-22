-- valueType definition
CREATE TABLE [valueType] (
   [type_id] TEXT PRIMARY KEY,
   [type_label] TEXT
);


-- valueDefinition definition
CREATE TABLE [valueDefinition] (
   [value_id] TEXT,
   [value_type_id] TEXT,
   [value_label] TEXT,
   PRIMARY KEY ([value_id], [value_type_id]),
   FOREIGN KEY([value_type_id]) REFERENCES [valueType]([type_id])
);

CREATE INDEX [idx_valueDefinition_value_type_id]
    ON [valueDefinition] ([value_type_id]);


-- parameterGroup definition
CREATE TABLE [parameterGroup] (
   [group_id] TEXT PRIMARY KEY,
   [group_label] TEXT,
   [group_entity] TEXT
);


-- parameterQuestion definition
CREATE TABLE [parameterQuestion] (
   [question_id] TEXT PRIMARY KEY,
   [question_label] TEXT,
   [question_statement_label] TEXT,
   [question_parent_id] TEXT,
   FOREIGN KEY([question_parent_id]) REFERENCES [parameterGroup]([group_id])
);

CREATE INDEX [idx_parameterQuestion_question_parent_id]
    ON [parameterQuestion] ([question_parent_id]);


-- parameterDefinition definition
CREATE TABLE [parameterDefinition] (
   [parameter_id] TEXT PRIMARY KEY,
   [parameter_name] TEXT,
   [parameter_group_id] TEXT,
   [parameter_value_type_id] TEXT,
   FOREIGN KEY([parameter_group_id]) REFERENCES [parameterQuestion]([question_id]),
   FOREIGN KEY([parameter_value_type_id]) REFERENCES [valueType]([type_id])
);

CREATE INDEX [idx_parameterDefinition_parameter_group_id]
    ON [parameterDefinition] ([parameter_group_id]);
CREATE INDEX [idx_parameterDefinition_parameter_value_type_id]
    ON [parameterDefinition] ([parameter_value_type_id]);


-- answerset definition
CREATE TABLE [answerset] (
   [answerset_id] TEXT PRIMARY KEY,
   [answerset_name] TEXT,
   [answerset_description] TEXT
);


-- answerset_data definition
CREATE TABLE [answerset_data] (
   [answerset_data_id] INTEGER PRIMARY KEY,
   [parameter_definition_id] TEXT,
   [value_shorttext] TEXT,
   [value_text] TEXT,
   [answerset] TEXT,
   FOREIGN KEY([answerset]) REFERENCES [answerset]([answerset_id]),
   FOREIGN KEY([parameter_definition_id]) REFERENCES [parameterDefinition]([parameter_id])
);

CREATE INDEX [idx_answerset_data_parameter_definition_id]
    ON [answerset_data] ([parameter_definition_id]);
CREATE INDEX [idx_answerset_data_answerset]
    ON [answerset_data] ([answerset]);


-- strategy definition
CREATE TABLE [strategy] (
   [strategy_id] INTEGER PRIMARY KEY,
   [strategy_name] TEXT COLLATE NOCASE,
   [strategy_description] TEXT COLLATE NOCASE,
   [strategy_answerset_id] TEXT,
   FOREIGN KEY([strategy_answerset_id]) REFERENCES [answerset]([answerset_id])
);

CREATE INDEX [idx_strategy_strategy_name]
    ON [strategy] ([strategy_name]);
CREATE INDEX [idx_strategy_strategy_description]
    ON [strategy] ([strategy_description]);
CREATE INDEX [idx_strategy_strategy_answerset_id]
    ON [strategy] ([strategy_answerset_id]);


-- strategy_data definition
CREATE TABLE [strategy_data] (
   [strategy_data_id] INTEGER PRIMARY KEY,
   [parameter_definition_id] TEXT,
   [value_shorttext] TEXT COLLATE NOCASE,
   [value_text] TEXT COLLATE NOCASE,
   [value_definition_id] TEXT,
   [strategy] INTEGER,
   FOREIGN KEY([parameter_definition_id]) REFERENCES [parameterDefinition]([parameter_id]),
   FOREIGN KEY([value_definition_id]) REFERENCES [valueDefinition]([value_id]),
   FOREIGN KEY([strategy]) REFERENCES [strategy]([strategy_id])
);

CREATE INDEX [idx_strategy_data_parameter_definition_id]
    ON [strategy_data] ([parameter_definition_id]);
CREATE INDEX [idx_strategy_data_value_shorttext]
    ON [strategy_data] ([value_shorttext]);
CREATE INDEX [idx_strategy_data_value_text]
    ON [strategy_data] ([value_text]);
CREATE INDEX [idx_strategy_data_value_definition_id]
    ON [strategy_data] ([value_definition_id]);
CREATE INDEX [idx_strategy_data_strategy]
    ON [strategy_data] ([strategy]);


-- sentence definition
CREATE TABLE [sentence] (
   [sentence_id] INTEGER PRIMARY KEY,
   [original] TEXT COLLATE NOCASE,
   [translation] TEXT COLLATE NOCASE,
   [gloss] TEXT COLLATE NOCASE,
   [grammaticality] TEXT,
   [sentence_answerset_id] TEXT,
   [sentence_strategy_id] INTEGER,
   FOREIGN KEY([sentence_answerset_id]) REFERENCES [answerset]([answerset_id]),
   FOREIGN KEY([sentence_strategy_id]) REFERENCES [strategy]([strategy_id])
);

CREATE INDEX [idx_sentence_sentence_answerset_id]
    ON [sentence] ([sentence_answerset_id]);
CREATE INDEX [idx_sentence_sentence_strategy_id]
    ON [sentence] ([sentence_strategy_id]);


-- sentence_data definition
CREATE TABLE [sentence_data] (
   [sentence_data_id] INTEGER PRIMARY KEY,
   [parameter_definition_id] TEXT,
   [value_text] TEXT COLLATE NOCASE,
   [value_definition_id] TEXT,
   [sentence_id] INTEGER,
   FOREIGN KEY([parameter_definition_id]) REFERENCES [parameterDefinition]([parameter_id]),
   FOREIGN KEY([value_definition_id]) REFERENCES [valueDefinition]([value_id]),
   FOREIGN KEY([sentence_id]) REFERENCES [sentence]([sentence_id])
);

CREATE INDEX [idx_sentence_data_parameter_definition_id]
    ON [sentence_data] ([parameter_definition_id]);
CREATE INDEX [idx_sentence_data_value_text]
    ON [sentence_data] ([value_text]);
CREATE INDEX [idx_sentence_data_value_definition_id]
    ON [sentence_data] ([value_definition_id]);
CREATE INDEX [idx_sentence_data_sentence_id]
    ON [sentence_data] ([sentence_id]);


/*
 * Use views for simpler queries in template_vars.py.
 */
CREATE VIEW IF NOT EXISTS strategy_data_all AS
WITH strategy_parameter_ids AS (
    SELECT DISTINCT sd.parameter_definition_id
    FROM strategy_data sd
    WHERE sd.parameter_definition_id != 'test10'
    ),
strategy_parameter_combinations AS (
    SELECT strategy_id, parameter_definition_id
    FROM strategy s
    CROSS JOIN strategy_parameter_ids sp
    )
-- Note: value_shorttext, value_text, and value_definition_id values are mutually exclusive in the database
SELECT spc.strategy_id
    , spc.parameter_definition_id
    , IFNULL(COALESCE(sd.value_shorttext, sd.value_text, sd.value_definition_id), '0') AS parameter_value
FROM strategy_parameter_combinations spc
LEFT JOIN strategy_data sd
 ON sd.parameter_definition_id = spc.parameter_definition_id
 AND sd.strategy = spc.strategy_id;


CREATE VIEW IF NOT EXISTS sentence_data_all AS
WITH sentence_parameter_ids AS (
    SELECT DISTINCT sd.parameter_definition_id
    FROM sentence_data sd
    ),
sentence_parameter_combinations AS (
    SELECT s.sentence_id, sp.parameter_definition_id, s.original, s."translation", s.gloss
    FROM sentence s
    CROSS JOIN sentence_parameter_ids sp
    )
-- Note: value_text and value_definition_id values are mutually exclusive in the database
SELECT spc.sentence_id
    , spc.parameter_definition_id
    , IFNULL(COALESCE(sd.value_text, sd.value_definition_id), '0') AS parameter_value
FROM sentence_parameter_combinations spc
LEFT JOIN sentence_data sd
 ON sd.parameter_definition_id = spc.parameter_definition_id
 AND sd.sentence_id = spc.sentence_id;


/*
 * The values in parameter_map are needed to join with other database values
 * in order to display the labels for searched parameters.
 * Note that part of the list contains the same values as the dicts defined in
 * template_vars.py, but there are differences for the keys which are not
 * referring to parameters in the _data tables.
 */
CREATE TABLE parameter_map (
  param_get text NOT NULL,
  param_db text NOT NULL
 );

INSERT INTO parameter_map
VALUES
('Alienability', 'Alienability1'),
('PossType', 'PossType1'),
('IdiomNotes', 'IdiomNotes1'),
('OpenAnimacy', 'OpenAnimacy1'),
('DODeterminer', 'DODeterminer1'),
('GenStructure', 'GenStructure1'),
('Modifier', 'Modifier1'),
('SpecialVerb', 'SpecialVerb1'),
('OpenPosition', 'OpenPosition1'),
('Aspect', 'Aspect1'),
('Modality', 'Modality1'),
('Tense', 'Tense1'),
('Voice', 'Voice1'),
('Judgments', 's:judgments1'),
('DeterminerManipulations', 'DeterminerManipulations1'),
('ExternalPossessionManipulation', 'ExternalPossessionManipulation'),
('FutureWordenManipulations', 'FutureWordenManipulations1'),
('ManipulatedProperty', 'Property1'),
('ModalityManipulations', 'ModalityManipulations1'),
('PossessiveManipulations', 'PossessiveManipulations1'),
('TenseVoiceAspectManipulations', 'TenseVoiceAspectManipulations1');


CREATE VIEW parameter_labels AS
WITH parameter_labels AS (
 SELECT
  pm.param_get AS param_get,
  pd.parameter_id AS parameter_id,
  pg.group_entity AS group_entity,
  pg.group_label AS group_label,
  COALESCE(pq.question_statement_label, pq.question_label) AS question_statement
 FROM parameterDefinition pd
 JOIN parameterQuestion pq
  ON pd.parameter_group_id = pq.question_id
 JOIN parameterGroup pg
  ON pq.question_parent_id = pg.group_id
JOIN parameter_map pm
 ON pm.param_db = pd.parameter_id
 WHERE pg.group_entity != 'answerset'
  AND pg.group_label != 'Translation'
  AND pd.parameter_id != 'test10'
  AND pd.parameter_id != 's:judgmentsCom'
 )
SELECT
 param_get,
 parameter_id,
 REPLACE(REPLACE(group_entity, 'strategy' , 'Idiom'), 'sentence', 'Sentence') AS group_entity,
 group_label,
 question_statement
FROM parameter_labels
UNION ALL
SELECT * FROM ( VALUES
  -- Values not available by JOINing.
  ('Dialect', NULL, 'Dialect', 'Dialect ID', NULL),
  ('Idiom', NULL, 'Idiom', 'Idiom', NULL),
  ('Meaning', NULL, 'Idiom', 'Meaning', NULL),
  ('Original', NULL, 'Sentence', 'Original', NULL),
  ('Gloss', NULL, 'Sentence', 'Gloss', NULL),
  ('Translation', NULL, 'Sentence', 'Translation', NULL),
  ('SentenceID', NULL, 'Sentence', 'Sentence ID', NULL)
 )
ORDER BY group_entity ASC, group_label ASC, question_statement ASC;
