"""Render data-derived findings, README metrics, and portfolio snapshot."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
import pandas as pd
from .config import ROOT, RAW_CSV, RAW_ARCHIVE, DB_PATH, PROFILE_JSON

def publish_reports(results:dict)->None:
    con=sqlite3.connect(DB_PATH)
    try:
        total,lo,hi=con.execute("SELECT COUNT(*),MIN(date_received),MAX(date_received) FROM fact_complaints").fetchone()
        timely_n,timely=con.execute("SELECT COUNT(timely_response_flag),AVG(timely_response_flag) FROM fact_complaints").fetchone()
        narrative,narrate_pct=con.execute("SELECT SUM(has_narrative),AVG(has_narrative) FROM fact_complaints").fetchone()
        top_company=con.execute("SELECT c.company,COUNT(*) n FROM fact_complaints f JOIN dim_company c USING(company_id) GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
        top_product=con.execute("SELECT p.product,COUNT(*) n FROM fact_complaints f JOIN dim_product p USING(product_id) GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
        top_issue=con.execute("SELECT i.issue,COUNT(*) n FROM fact_complaints f JOIN dim_issue i USING(issue_id) GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
        top_state=con.execute("SELECT g.state,COUNT(*) n FROM fact_complaints f JOIN dim_geography g USING(state_id) GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
        top_channel=con.execute("SELECT ch.submitted_via,COUNT(*) n FROM fact_complaints f JOIN dim_channel ch USING(channel_id) GROUP BY 1 ORDER BY n DESC LIMIT 1").fetchone()
        responses=con.execute("SELECT AVG(response_days),COUNT(response_days) FROM fact_complaints WHERE response_days>=0").fetchone()
        top10=con.execute("WITH c AS(SELECT company_id,COUNT(*) n FROM fact_complaints GROUP BY 1),r AS(SELECT n,ROW_NUMBER() OVER(ORDER BY n DESC) rn FROM c) SELECT SUM(CASE WHEN rn<=10 THEN n ELSE 0 END)*1.0/(SELECT COUNT(*) FROM fact_complaints) FROM r").fetchone()[0]
        years=con.execute("SELECT year,COUNT(*) FROM fact_complaints WHERE year IS NOT NULL GROUP BY 1 ORDER BY 1").fetchall()
    finally:con.close()
    def share(n):return n/total if total else 0
    nfind=[
      (f"The analytical fact table contains {total:,} unique complaints received from {lo} through {hi}.","All retained complaint records and date coverage.","COUNT(*) and MIN/MAX(date_received) from fact_complaints.","This is the observable CFPB publication database for this source snapshot.","CFPB notes the database is not representative of all consumer experiences."),
      (f"{top_product[0]} is the largest product category with {top_product[1]:,} complaints ({share(top_product[1]):.1%} of retained records).",f"Product: {top_product[0]}.","Product-group complaint count divided by total fact rows.","This product represents the largest observed published complaint workload.","Counts do not adjust for product customers, market share, or risk exposure."),
      (f"{top_issue[0]} is the most frequent issue, with {top_issue[1]:,} complaints ({share(top_issue[1]):.1%}).",f"Issue: {top_issue[0]}.","Issue-group complaint count divided by total fact rows.","This issue is a useful starting point for operational deep dives.","Complaint categories and publication rates can change across time."),
      (f"{top_company[0]} has the highest observed company count: {top_company[1]:,} ({share(top_company[1]):.1%} of all records).",f"Company: {top_company[0]}.","Company complaint count divided by total fact rows.","Volume can guide case-management workload review.","This is not a company quality ranking and is not normalized by customer base or market share."),
      (f"Among {timely_n:,} complaints with a known timely-response flag, {timely:.1%} are marked timely.","All years, known timely-response flag only.","AVG(timely_response_flag) over non-null flags.","This summarizes the operational indicator recorded in the published database.","Unknown flags are excluded; publication rules affect the observed mix."),
      (f"{narrative:,} records ({narrate_pct:.1%}) include a published consumer narrative.","All retained records.","SUM(has_narrative) and AVG(has_narrative).","Narratives enable qualitative theme exploration for a subset.","Availability is selective and should not be generalized to all complaints."),
      (f"{top_state[0]} has the most records by reported state: {top_state[1]:,} ({share(top_state[1]):.1%}).",f"Reported state: {top_state[0]}.","State complaint count divided by total fact rows.","State volume can help scope regional operational research.","No population adjustment; counts are not per-capita rates."),
      (f"{top_channel[0]} is the most used submission channel with {top_channel[1]:,} complaints ({share(top_channel[1]):.1%}).",f"Channel: {top_channel[0]}.","Channel count divided by total fact rows.","Channel mix informs intake and digital support planning.","Channel availability and consumer preferences can shift over time."),
      (f"The ten largest companies account for {top10:.1%} of complaint records.","Company concentration over all dates.","Top-ten company complaint sum divided by fact row count.","A limited set of large-volume entities shapes a material share of service workload.","Company size and market share are not available as denominators."),
      (f"Mean elapsed days from received to sent-to-company is {responses[0]:.1f} days across {responses[1]:,} valid dated records.","Records with a nonnegative response_days value.","AVG(date_sent_to_company - date_received) in whole calendar days.","This is a simple routing-time proxy that can flag unusual shifts.","It is not a complete measure of resolution time or consumer satisfaction."),
    ]
    growth=pd.read_csv(ROOT/"outputs/tables/04_year_over_year_growth.csv").dropna(subset=["prior_year"]) if (ROOT/"outputs/tables/04_year_over_year_growth.csv").exists() else pd.DataFrame()
    if len(growth):
        latest=growth.iloc[-1]; nfind.append((f"Published complaints changed {latest['change_pct']:.1%} in {int(latest.year)} versus {int(latest.year)-1} ({int(latest.complaints):,} vs {int(latest.prior_year):,}).",f"Calendar years {int(latest.year)-1} and {int(latest.year)}.","Annual count difference divided by prior-year count.","Year-over-year change indicates a shift in published complaint workload.","The newest year may be incomplete; reporting and publication processes can change."))
    emerging=pd.read_csv(ROOT/"outputs/tables/15_issue_year_growth.csv") if (ROOT/"outputs/tables/15_issue_year_growth.csv").exists() else pd.DataFrame()
    if len(emerging):
        latest_year=emerging.year.max(); subset=emerging[emerging.year==latest_year].dropna(subset=["growth_pct"])
        if len(subset):
            hit=subset.sort_values("growth_pct",ascending=False).iloc[0]
            nfind.append((f"{hit.issue} increased {hit.growth_pct:.1%} in {int(hit.year)} on a prior-year base of {int(hit.prev):,} complaints.",f"Issue: {hit.issue}; year {int(hit.year)}.","Year-over-year issue count growth, limited to prior-year count ≥100.","This is a candidate emerging issue for follow-up with absolute counts and context.","A latest calendar year may be partial; growth does not establish cause or harm severity."))
    lines=["# Analysis Findings","",f"Data snapshot: {lo} to {hi}; {total:,} cleaned records.","","> CFPB complaint counts are not representative consumer incidence or company quality. Company-size/market-share and population denominators are absent.",""]
    for i,(metric,period,calc,interpretation,caution) in enumerate(nfind,1):
        lines += [f"## {i}. {metric}","",f"- Period/segment: {period}",f"- Calculation: {calc}",f"- Business interpretation: {interpretation}",f"- Limitation: {caution}",""]
    (ROOT/"docs/ANALYSIS_FINDINGS.md").write_text("\n".join(lines),encoding="utf-8")
    profile=json.loads(PROFILE_JSON.read_text(encoding="utf-8"))
    readme=ROOT/"README.md"; txt=readme.read_text(encoding="utf-8")
    size=f"\n- Raw rows profiled: **{profile['rows']:,}**\n- Clean unique complaint rows: **{total:,}**\n- Date coverage: **{lo} to {hi}**\n- Raw extracted CSV: **{RAW_CSV.stat().st_size:,} bytes**; ZIP archive: **{RAW_ARCHIVE.stat().st_size:,} bytes**\n- SQLite database: **{(ROOT/'database/complaints.db').stat().st_size:,} bytes**\n- Power BI fact export: **{(ROOT/'data/powerbi/fact_complaints.parquet').stat().st_size:,} bytes**\n"
    txt=txt.replace("Generated from the completed pipeline in `outputs/reports/pipeline_run.json` and `outputs/reports/validation_report.txt`. Statistics are never hard-coded or fabricated.",size)
    readme.write_text(txt,encoding="utf-8")
    psummary=(ROOT/"docs/PORTFOLIO_SUMMARY.md").read_text(encoding="utf-8")
    psummary=psummary.replace("This file is completed with observed dataset size and calculated results after running the end-to-end pipeline. It should not be populated with assumed metrics.",f"Executed on the official CFPB data snapshot covering {lo} to {hi}; {total:,} clean records were processed.")
    psummary += f"\n\n## Observed results\n\nThe largest product by count is {top_product[0]} ({top_product[1]:,}); the most frequent issue is {top_issue[0]} ({top_issue[1]:,}); known timely response rate is {timely:.1%} across {timely_n:,} records; published narratives appear in {narrate_pct:.1%} of records. These counts describe the published database and do not adjust for market share or population.\n"
    (ROOT/"docs/PORTFOLIO_SUMMARY.md").write_text(psummary,encoding="utf-8")
