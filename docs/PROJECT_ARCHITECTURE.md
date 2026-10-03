# Project Architecture

The pipeline uses the official CFPB all-record ZIP as an immutable input. Streaming profiling executes before transformations. Chunked pandas processing standardizes fields and emits Parquet parts; feature engineering adds complaint-level calendar, response, and narrative attributes. SQLite is built from those parts using a fact table with integer foreign keys to date, company, product, issue, state, and channel dimensions. SQL analyses and visual aggregates read the analytical database. Narrative TF-IDF/NMF is performed separately on a documented deterministic corpus cap. Power BI receives a full-row Parquet fact and dimension CSVs. Critical row counts, uniqueness, foreign keys, date validity, and SQL/Python/export reconciliations are checked at the end.

The pipeline is modular under `src/`; paths and chunk size live in `src/config.py`; SQL DDL/indexes/business queries are under `sql/`. Generated artifacts go to `outputs/`, `database/`, and `data/powerbi/`.
