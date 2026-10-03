# Power BI data exports

Import `fact_complaints.parquet` with **Get data → Parquet**. Import each `dim_*.csv` through **Text/CSV**. Keep all rows; these are full-data exports. In Power Query, set `date_received` and `date_sent_to_company` to Date, complaint and ZIP identifiers to Text, and metric/foreign-key fields to Whole number. Relate integer keys as documented in `../../powerbi/POWER_BI_MODEL.md`. `complaints.db` in the repository's database folder is also available for SQLite-capable connectors.

The narrative column contains the CFPB public narrative text when consumers consented. Handle it as consumer-provided text and retain the published data cautions.
