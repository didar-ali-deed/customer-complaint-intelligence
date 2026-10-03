# Power BI DAX Measures

Create these measures on `fact_complaints`. They use the active `dim_date[date]` relationship. Set count measures to whole number and rates to percentage with one decimal place.

```DAX
Total Complaints = DISTINCTCOUNT(fact_complaints[complaint_id])

Complaints Previous Month =
CALCULATE([Total Complaints], DATEADD(dim_date[date], -1, MONTH))

MoM Change = [Total Complaints] - [Complaints Previous Month]

MoM Change % = DIVIDE([MoM Change], [Complaints Previous Month])

Complaints Previous Year =
CALCULATE([Total Complaints], DATEADD(dim_date[date], -1, YEAR))

YoY Change = [Total Complaints] - [Complaints Previous Year]

YoY Change % = DIVIDE([YoY Change], [Complaints Previous Year])

Timely Responses =
CALCULATE([Total Complaints], fact_complaints[timely_response_flag] = 1)

Timely Response % =
DIVIDE([Timely Responses],
    CALCULATE([Total Complaints], FILTER(fact_complaints, NOT ISBLANK(fact_complaints[timely_response_flag]))))

Complaints With Narratives =
CALCULATE([Total Complaints], fact_complaints[has_narrative] = 1)

Narrative Rate % = DIVIDE([Complaints With Narratives], [Total Complaints])

Company Public Responses =
CALCULATE([Total Complaints],
    FILTER(fact_complaints,
        NOT ISBLANK(fact_complaints[company_public_response]) &&
        LEN(TRIM(fact_complaints[company_public_response])) > 0))

Company Public Response Rate % = DIVIDE([Company Public Responses], [Total Complaints])

Unique Companies = DISTINCTCOUNT(fact_complaints[company_id])
Unique Products = DISTINCTCOUNT(fact_complaints[product_id])
Unique Issues = DISTINCTCOUNT(fact_complaints[issue_id])

Average Response Days =
CALCULATE(AVERAGE(fact_complaints[response_days]), fact_complaints[response_days] >= 0)

Rolling 3 Month Complaints =
CALCULATE([Total Complaints], DATESINPERIOD(dim_date[date], MAX(dim_date[date]), -3, MONTH))

Rolling 12 Month Complaints =
CALCULATE([Total Complaints], DATESINPERIOD(dim_date[date], MAX(dim_date[date]), -12, MONTH))

Selected Period Complaints = [Total Complaints]

Company Complaint Share % =
DIVIDE([Total Complaints], CALCULATE([Total Complaints], REMOVEFILTERS(dim_company)))

Product Complaint Share % =
DIVIDE([Total Complaints], CALCULATE([Total Complaints], REMOVEFILTERS(dim_product)))

Issue Complaint Share % =
DIVIDE([Total Complaints], CALCULATE([Total Complaints], REMOVEFILTERS(dim_issue)))

Narrative Average Words =
CALCULATE(AVERAGE(fact_complaints[narrative_word_count]), fact_complaints[has_narrative] = 1)

Complaints Prior Rolling Year =
CALCULATE([Total Complaints], DATEADD(dim_date[date], -1, YEAR))
```

For executive comparisons, filter to a complete date period; the newest partial month/year can make growth appear unusually high or low. `[Selected Period Complaints]` follows current report filters by design. Complaint share removes only the selected segment's filter and retains date, geography, and other slicers.
