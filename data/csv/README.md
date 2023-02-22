# Database contents

SQLite was chosen for its ease of maintenance, the security benefits of a read-only database, and archivability.
In principle this data set is frozen, but in order to allow fixing typos or small coding mistakes, it is bundled with the repository in the form of tab-separated values (TSV) files, from which the SQLite database is created.
To update a record, check the idiom or sentence ID in the URL by visiting its detail page, then find the corresponding `.tsv` file and make sure to look up the ID in the correct column (e.g. for _data tables, the column referencing the parent table).
