# Power BI Data Model

## Import and relationships

Import `data/powerbi/fact_complaints.parquet` and all six `dim_*.csv` files. Use a single-direction, active, one-to-many relationship from each dimension's key to the corresponding fact key:

| Dimension (one side) | Fact (many side) | Type | Direction |
|---|---|---|---|
| `dim_date[date_key]` | `fact_complaints[date_key]` | 1:* | Single |
| `dim_company[company_id]` | `fact_complaints[company_id]` | 1:* | Single |
| `dim_product[product_id]` | `fact_complaints[product_id]` | 1:* | Single |
| `dim_issue[issue_id]` | `fact_complaints[issue_id]` | 1:* | Single |
| `dim_geography[state_id]` | `fact_complaints[state_id]` | 1:* | Single |
| `dim_channel[channel_id]` | `fact_complaints[channel_id]` | 1:* | Single |

Set keys to Whole number. Treat `complaint_id`, `zip_code`, and categorical/text columns as Text; set dates to Date and measures to Whole number or decimal. `date_received` and `date_key` describe the same role: use `dim_date` for all time filtering and keep `date_key` relationship active. The sent date is a separate role-playing date; leave inactive unless adding an explicit USERELATIONSHIP measure.

Mark `dim_date` as the date table using `[date]`. Sort `month_name` by `month`; sort `year_month` in the fact by its chronological text key (ISO `YYYY-MM`). Sort weekday labels with a custom 1–7 weekday sort column if used. Hide surrogate keys, raw date keys, and duplicate fact date parts from report view. Keep complaint narratives out of standard visuals and enable drill-through to inspect individual narrative records carefully.

## Model cautions

The records are complaints CFPB publishes under its process, not a representative sample of consumer experience. Raw company/product counts are not quality rates and lack customer/market-share denominators. Compare timely-response percentages only among records with a known flag; company rankings should expose the complaint-count floor used. ZIP/state counts need population context. Narrative text exists only for records with published consent and should not be treated as a complete or unbiased subset.
