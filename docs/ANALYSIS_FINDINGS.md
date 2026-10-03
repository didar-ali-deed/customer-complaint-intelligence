# Analysis Findings

Data snapshot: 2011-12-01 to 2026-10-02; 18,145,013 cleaned records.

> CFPB complaint counts are not representative consumer incidence or company quality. Company-size/market-share and population denominators are absent.

## 1. The analytical fact table contains 18,145,013 unique complaints received from 2011-12-01 through 2026-10-02.

- Period/segment: All retained complaint records and date coverage.
- Calculation: COUNT(*) and MIN/MAX(date_received) from fact_complaints.
- Business interpretation: This is the observable CFPB publication database for this source snapshot.
- Limitation: CFPB notes the database is not representative of all consumer experiences.

## 2. Credit reporting or other personal consumer reports is the largest product category with 12,555,681 complaints (69.2% of retained records).

- Period/segment: Product: Credit reporting or other personal consumer reports.
- Calculation: Product-group complaint count divided by total fact rows.
- Business interpretation: This product represents the largest observed published complaint workload.
- Limitation: Counts do not adjust for product customers, market share, or risk exposure.

## 3. Incorrect information on your report is the most frequent issue, with 8,232,996 complaints (45.4%).

- Period/segment: Issue: Incorrect information on your report.
- Calculation: Issue-group complaint count divided by total fact rows.
- Business interpretation: This issue is a useful starting point for operational deep dives.
- Limitation: Complaint categories and publication rates can change across time.

## 4. TRANSUNION INTERMEDIATE HOLDINGS, INC. has the highest observed company count: 5,015,681 (27.6% of all records).

- Period/segment: Company: TRANSUNION INTERMEDIATE HOLDINGS, INC..
- Calculation: Company complaint count divided by total fact rows.
- Business interpretation: Volume can guide case-management workload review.
- Limitation: This is not a company quality ranking and is not normalized by customer base or market share.

## 5. Among 18,145,013 complaints with a known timely-response flag, 99.4% are marked timely.

- Period/segment: All years, known timely-response flag only.
- Calculation: AVG(timely_response_flag) over non-null flags.
- Business interpretation: This summarizes the operational indicator recorded in the published database.
- Limitation: Unknown flags are excluded; publication rules affect the observed mix.

## 6. 0 records (0.0%) include a published consumer narrative in this CFPB release.

- Period/segment: All retained records.
- Calculation: SUM(has_narrative) and AVG(has_narrative).
- Business interpretation: The current downloadable release provides no consumer narrative field; NLP therefore uses the separate company public-response field.
- Limitation: Company response statements do not represent consumer language or consumer sentiment.

## 7. 9,993,441 complaints (55.1%) contain CFPB-published company public-response text.

- Period/segment: All retained records.
- Calculation: Non-empty company_public_response count divided by all fact rows.
- Business interpretation: The field supports a separate analysis of published company statements.
- Limitation: This text is not the consumer complaint narrative and cannot support claims about consumer sentiment.

## 8. TX has the most records by reported state: 2,509,581 (13.8%).

- Period/segment: Reported state: TX.
- Calculation: State complaint count divided by total fact rows.
- Business interpretation: State volume can help scope regional operational research.
- Limitation: No population adjustment; counts are not per-capita rates.

## 9. Web is the most used submission channel with 17,507,111 complaints (96.5%).

- Period/segment: Channel: Web.
- Calculation: Channel count divided by total fact rows.
- Business interpretation: Channel mix informs intake and digital support planning.
- Limitation: Channel availability and consumer preferences can shift over time.

## 10. The ten largest companies account for 84.0% of complaint records.

- Period/segment: Company concentration over all dates.
- Calculation: Top-ten company complaint sum divided by fact row count.
- Business interpretation: A limited set of large-volume entities shapes a material share of service workload.
- Limitation: Company size and market share are not available as denominators.

## 11. Mean elapsed days from received to sent-to-company is 0.6 days across 18,137,963 valid dated records.

- Period/segment: Records with a nonnegative response_days value.
- Calculation: AVG(date_sent_to_company - date_received) in whole calendar days.
- Business interpretation: This is a simple routing-time proxy that can flag unusual shifts.
- Limitation: It is not a complete measure of resolution time or consumer satisfaction.

## 12. Through 2026-10-02, published complaints changed 38.1% versus the same period through 2025-10-02 (5,462,631 vs 3,955,757).

- Period/segment: Year-to-date through 2026-10-02 compared with the same month/day in the prior year.
- Calculation: Matched-period year-to-date totals; current cutoff is the latest received date in the source.
- Business interpretation: This comparison controls for the current year being partial.
- Limitation: CFPB publication and category practices may vary over time.

## 13. Took or threatened to take negative or legal action increased 121.8% through 2026-10-02 versus the same period through 2025-10-02 (55,175 vs 24,872).

- Period/segment: Issue: Took or threatened to take negative or legal action; matched year-to-date periods.
- Calculation: Issue complaint growth on the same month/day cutoff, restricted to prior-period count ≥100.
- Business interpretation: This is a candidate emerging issue for follow-up with absolute counts and operational context.
- Limitation: Publication patterns and category definitions can shift; volume change alone does not establish cause or harm severity.
