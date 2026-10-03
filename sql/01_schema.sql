DROP TABLE IF EXISTS fact_complaints;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_company;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_issue;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_channel;
CREATE TABLE dim_date(date_key INTEGER PRIMARY KEY, date TEXT UNIQUE NOT NULL, year INTEGER, quarter INTEGER, month INTEGER, month_name TEXT, year_month TEXT, week INTEGER, day_of_week TEXT, day_of_week_sort INTEGER);
CREATE TABLE dim_company(company_id INTEGER PRIMARY KEY, company TEXT UNIQUE NOT NULL);
CREATE TABLE dim_product(product_id INTEGER PRIMARY KEY, product TEXT UNIQUE NOT NULL);
CREATE TABLE dim_issue(issue_id INTEGER PRIMARY KEY, issue TEXT UNIQUE NOT NULL);
CREATE TABLE dim_geography(state_id INTEGER PRIMARY KEY, state TEXT UNIQUE NOT NULL);
CREATE TABLE dim_channel(channel_id INTEGER PRIMARY KEY, submitted_via TEXT UNIQUE NOT NULL);
CREATE TABLE fact_complaints(
 complaint_id TEXT PRIMARY KEY, date_key INTEGER, company_id INTEGER, product_id INTEGER, issue_id INTEGER, state_id INTEGER, channel_id INTEGER,
 date_received TEXT, date_sent_to_company TEXT, sub_product TEXT, sub_issue TEXT, zip_code TEXT, tags TEXT,
 consumer_consent_provided TEXT, company_response_to_consumer TEXT, timely_response TEXT, consumer_disputed TEXT,
 consumer_complaint_narrative TEXT, year INTEGER, quarter INTEGER, month INTEGER, month_name TEXT, year_month TEXT,
 week INTEGER, day_of_week TEXT, response_days INTEGER, timely_response_flag INTEGER, has_narrative INTEGER,
 narrative_length INTEGER, narrative_word_count INTEGER,
 FOREIGN KEY(date_key) REFERENCES dim_date(date_key), FOREIGN KEY(company_id) REFERENCES dim_company(company_id),
 FOREIGN KEY(product_id) REFERENCES dim_product(product_id), FOREIGN KEY(issue_id) REFERENCES dim_issue(issue_id),
 FOREIGN KEY(state_id) REFERENCES dim_geography(state_id), FOREIGN KEY(channel_id) REFERENCES dim_channel(channel_id));
