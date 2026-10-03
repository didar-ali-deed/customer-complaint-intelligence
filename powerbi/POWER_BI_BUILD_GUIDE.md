# Power BI Desktop Build Guide

1. Run `python -m src.run_pipeline` and wait for the validation report to show `PASS`.
2. Open Power BI Desktop and choose **Get data → Parquet**. Select `data/powerbi/fact_complaints.parquet`.
3. Choose **Get data → Text/CSV** and import each of `dim_date.csv`, `dim_company.csv`, `dim_product.csv`, `dim_issue.csv`, `dim_geography.csv`, and `dim_channel.csv` from the same folder. Load `narrative_top_terms.csv`, `narrative_terms_by_segment.csv`, and `narrative_topics.csv` only for Page 5.
4. Select **Transform data**. In Power Query set `complaint_id`, `zip_code`, states, and category fields to Text; key and count fields to Whole number; response measures to Decimal; and received/sent dates to Date. Keep narrative as Text. Do not replace absent narratives with invented content.
5. Close & Apply. In Model view create active one-to-many single-direction relationships listed in `POWER_BI_MODEL.md`; dimension keys go on the one side. Check that each dimension key is unique and all fact foreign keys match.
6. Select `dim_date`, choose **Mark as date table**, and select its `[date]` field. Use the provided daily date dimension; do not generate a second calendar table.
7. In Report view create the DAX measures in `POWER_BI_MEASURES.md`. Set rate measures to Percentage (one decimal), counts to whole number with thousands separators, and response days to one decimal.
8. In Data view sort `dim_date[month_name]` by `[month]`. Sort the fact's ISO `year_month` ascending; use the date dimension's year/month hierarchy for period navigation.
9. Build Page 1 with five KPI cards, monthly trend, product/company rankings, state map, and date/product/state/channel slicers. Add the published caveat as a visible footer.
10. Build Page 2 with product and issue rankings, product-by-issue matrix, complete-period growth comparisons, and drill-through to complaint detail.
11. Build Page 3 with company counts, timely response rate and denominator, company trends, company-by-product matrix, and response categories.
12. Build Page 4 with state map/ranking, channel breakdown and trend, and state-by-product matrix. Retain unknown-state records outside the map.
13. Build Page 5 with consumer narrative coverage (zero for this source release), company public-response categories, top terms, segment terms, and NMF topic terms. Add a note that NLP uses a capped sample of company public-response text and describes CFPB-published company statements, not consumer sentiment.
14. Configure slicer synchronization, cross-highlighting, drill-through, and report tooltips. Keep optional bookmarks limited to useful count/rate views.
15. Apply a consistent 16:9 theme, readable labels, restrained colors, short titles, and conditional formatting as described in `POWER_BI_VISUAL_PLAN.md`.
16. Reconcile the all-time complaint card to the `fact_complaints` row count in `outputs/reports/validation_report.txt`. Check year totals and timely-response denominators against SQL exports under `outputs/tables/`.
17. Save the report as `powerbi/Customer_Complaint_Intelligence.pbix`. Export page screenshots for the README after reviewing privacy and visual legibility.

The Power BI file is intentionally left for the project owner to create in Power BI Desktop.
