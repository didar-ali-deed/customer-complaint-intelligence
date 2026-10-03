# Raw Data Quality Report

- Rows: 18,145,013
- Columns: 15
- Raw parser dtypes: all string values to preserve identifiers and ZIP codes.
- Estimated cumulative parsed memory across 100,000-row chunks: 20,712,097,816 bytes (not peak memory).
- Duplicate complaint IDs found within chunks: 0
- Exact duplicate rows found across the streamed source: 0
- Invalid state-code rows before cleaning: 1,522
- Unexpected values in available yes/no fields: 0
- Non-two-letter states are normalized to null during cleaning; valid complaint rows are retained.
- Date ranges: `{"Date sent to company": {"min": "2011-12-01T00:00:00", "max": "2026-10-02T00:00:00"}, "Date received": {"min": "2011-12-01T00:00:00", "max": "2026-10-02T00:00:00"}}`
- Malformed dates: `{"Date sent to company": 0, "Date received": 0}`
- CFPB expected fields absent from this release: Consumer complaint narrative, Consumer consent provided?, Consumer disputed?.
- Whitespace anomalies by column: `{"Company": 24}`
- Case-only variant groups in audited categories: `{}`
- Available text-field measurements: `{"Company public response_nonempty": 9993441, "Company public response_characters": 939768133, "Company response to consumer_nonempty": 18144992, "Company response to consumer_characters": 458823607, "Timely response?_nonempty": 18145013, "Timely response?_characters": 54324816}`

## Missing values

                      column  missing_count  missing_pct
                        Tags       17330239      95.5097
     Company public response        8151572      44.9246
                   Sub-issue         938987       5.1749
                 Sub-product         235275       1.2966
                       State          63036       0.3474
                    ZIP code           2859       0.0158
Company response to consumer             21       0.0001
                       Issue              6       0.0000

## Column profile

See `outputs/reports/raw_data_profile.csv` for each field's raw type, missing count and percentage, exact/estimated cardinality, whitespace count, category case-variant groups, and example values.

## Profiling notes

Profiling completes before cleaning. Low-cardinality counts are exact; high-cardinality counts use bounded-memory HyperLogLog estimates (p=12). Exact row fingerprints are compared across streamed records. The raw CSV is preserved unchanged; missing source fields are not inferred or fabricated.
