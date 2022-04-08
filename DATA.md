# Pages

Document the data structures/sources used for generating the pages in the old application.

## Browse

- list, answerset
--> Table: answerset
answerset_name: Name
answerset_description: Principal Location
- detail, answerset_id, answerset
    - Page title: Dialect > Answerset/dialect Name >> Location (duplicate?)
        - Custom Properties > Dialect information > Principal location, Source
        - Manipulations
        List manipulations [link] --> Sentences
        - Idioms
        xxx records found.
        Columns: [Number], Idiom, Meaning, Dialect, Properties
        --> Table: strategy
        --> Properties links to: Table: strategy_data
- list, sentence
--> Table: sentences


sentence.original = strategy.strategy_name [duplicate?]
sentence.sentence_answerset_id = strategy.strategy_answerset_id [duplicate?]
sentence.sentence_strategy_id = strategy.strategy_id [FK]

