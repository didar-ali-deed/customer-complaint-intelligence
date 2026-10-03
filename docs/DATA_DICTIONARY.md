# Data Dictionary

Raw fields are converted from CFPB headers to lowercase snake_case. Common fields include `complaint_id` (string identifier), `date_received`, `date_sent_to_company`, `product`, `sub_product`, `issue`, `sub_issue`, `company`, `state` (two-letter code where valid), `zip_code` (string), `tags`, `consumer_consent_provided`, `submitted_via`, `company_response_to_consumer`, `timely_response`, `consumer_disputed`, and `consumer_complaint_narrative`.

Derived fields include calendar parts (`year`, `quarter`, `month`, `month_name`, `year_month`, `week`, `day_of_week`), `response_days` (nonnegative elapsed date difference), `timely_response_flag` (1/0/null), `has_narrative`, `narrative_length` (characters), and `narrative_word_count`. SQLite surrogate keys connect fact records to dimensions. For complete observed categories and exact types, use generated `outputs/reports/raw_data_profile.csv` and database schema `sql/01_schema.sql`.
