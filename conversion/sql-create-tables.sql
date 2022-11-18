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
   [sentence] INTEGER,
   FOREIGN KEY([parameter_definition_id]) REFERENCES [parameterDefinition]([parameter_id]),
   FOREIGN KEY([value_definition_id]) REFERENCES [valueDefinition]([value_id]),
   FOREIGN KEY([sentence]) REFERENCES [sentence]([sentence_id])
);

CREATE INDEX [idx_sentence_data_parameter_definition_id]
    ON [sentence_data] ([parameter_definition_id]);
CREATE INDEX [idx_sentence_data_value_text]
    ON [sentence_data] ([value_text]);
CREATE INDEX [idx_sentence_data_value_definition_id]
    ON [sentence_data] ([value_definition_id]);
CREATE INDEX [idx_sentence_data_sentence]
    ON [sentence_data] ([sentence]);
