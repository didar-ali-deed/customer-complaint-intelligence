# Power BI Visual Plan

Use a 16:9 canvas, restrained navy/teal palette, consistent date slicer, concise titles, and tooltips with count, share, and period context. Use `dim_date[year_month]` for monthly axes. Add a persistent footer: “CFPB complaints are not a representative sample. Counts are not adjusted for customer base or market share.”

## Page 1 — Executive Overview

Cards: `[Total Complaints]`, `[YoY Change %]`, `[Timely Response %]`, `[Unique Companies]`, `[Narrative Rate %]`. Line chart: Axis `dim_date[year_month]` (sort chronologically), Values `[Total Complaints]`, tooltip rolling-12-month. Clustered bar: product by `[Total Complaints]`, top 10. Bar chart: company by complaints, top 10 and minimum count caveat. Filled map: `dim_geography[state]`, location state, color `[Total Complaints]`; exclude null state. Slicers: year/date, product, state, channel. Cross-filter charts; card selections follow filters.

## Page 2 — Product & Issue Analysis

Ranked horizontal bars: product and issue, Values complaints and share measures. Matrix: Rows product, Columns issue, Values `[Total Complaints]`, conditional-format background. Line chart: year_month, complaints, small multiples by leading products. Emerging issue bar chart: issue/year with latest complete year and prior year, filter prior-year count ≥100; show absolute delta alongside growth rate to expose small-base effects. Drill-through to detail page with company, issue, monthly trend, and complaint IDs.

## Page 3 — Company Performance

Company ranking bar: complaints with top-N and explicit count threshold. Scatter: X complaints, Y `[Timely Response %]`, size narratives, legend product only when focused; tooltip company and period. Line chart: monthly complaints, legend selected company. Matrix: company × product with complaints and timely response. Stacked bar: `company_response_to_consumer` by count. Use a denominator tooltip for all rates; avoid labeling volume as quality.

## Page 4 — Geography & Channels

Filled map: state location, complaints as color, tooltip count and selected period. Ranked state bar; line by month with state slicer. Bar chart: `dim_channel[submitted_via]`, complaints and share. Line chart: month axis, complaints, legend channel. Matrix: state × product with count and timely percentage. Filter unknown geography for the map only; retain an unknown category in other visuals.

## Page 5 — Narrative Intelligence

Cards: narratives, narrative rate, average words. Line chart: year and narrative rate. Bar: average/median narrative words by product using narrative rows. Table: top TF-IDF terms from `outputs/tables/narrative_top_terms.csv`; bar/matrix: precomputed top terms by product/issue from `narrative_terms_by_segment.csv`; table topics from `narrative_topics.csv`. These NLP outputs are computed on the documented capped corpus and are investigative aids, not objective sentiment. Avoid placing raw narrative text on summary pages.

Use report-page tooltips for company response denominator, product/issue context, and narrative coverage. Add drill-through from company/product/issue to detail. Bookmarks are optional for switching count vs response-rate perspectives; avoid decorative navigation that competes with analysis. Conditional formatting should use diverging colors centered on zero for growth and a sequential palette for volume. Synchronize date slicers across pages; allow page-specific geography and narrative filters.
