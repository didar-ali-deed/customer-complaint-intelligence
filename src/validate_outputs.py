"""Fail on critical integrity errors and reconcile source, fact, SQL, and exports."""
from __future__ import annotations
import json, sqlite3
from datetime import date
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from .config import DB_PATH, CLEAN_DIR, ROOT, RAW_CSV, RAW_ARCHIVE

def validate_outputs(db_path:Path=DB_PATH)->dict:
    checks=[]
    def add(name,passed,detail): checks.append({"check":name,"status":"PASS" if passed else "FAIL","detail":str(detail)})
    parts=sorted(CLEAN_DIR.glob("part-*.parquet")); clean=sum(pq.ParquetFile(p).metadata.num_rows for p in parts)
    con=sqlite3.connect(db_path)
    try:
        fact=con.execute("SELECT COUNT(*) FROM fact_complaints").fetchone()[0]
        unique=con.execute("SELECT COUNT(DISTINCT complaint_id) FROM fact_complaints").fetchone()[0]
        bad_date=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE date_received IS NOT NULL AND date(date_received) IS NULL").fetchone()[0]
        future=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE date_received>date('now')").fetchone()[0]
        missing_key=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE complaint_id IS NULL OR date_received IS NULL").fetchone()[0]
        orphan=con.execute("SELECT COUNT(*) FROM fact_complaints f LEFT JOIN dim_company c USING(company_id) WHERE f.company_id IS NOT NULL AND c.company_id IS NULL").fetchone()[0]
        bad_boolean=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE timely_response_flag NOT IN (0,1) AND timely_response_flag IS NOT NULL").fetchone()[0]
        add("clean-to-database row reconciliation",clean==fact,f"clean={clean:,}; database={fact:,}")
        add("complaint ID uniqueness",fact==unique,f"rows={fact:,}; unique IDs={unique:,}")
        add("date parsing",bad_date==0,f"malformed non-null database dates={bad_date:,}")
        add("future received dates",future==0,f"future dates={future:,}")
        add("required complaint/date fields",missing_key==0,f"missing required fields={missing_key:,}")
        add("company dimension integrity",orphan==0,f"orphan foreign keys={orphan:,}")
        for key,dimension in [("date_key","dim_date"),("product_id","dim_product"),("issue_id","dim_issue"),("state_id","dim_geography"),("channel_id","dim_channel")]:
            invalid=con.execute(f"SELECT COUNT(*) FROM fact_complaints f LEFT JOIN {dimension} d USING({key}) WHERE f.{key} IS NOT NULL AND d.{key} IS NULL").fetchone()[0]
            add(f"{dimension} referential integrity",invalid==0,f"orphan foreign keys={invalid:,}")
        add("timely response flags",bad_boolean==0,f"invalid flags={bad_boolean:,}")
        invalid_yes_no=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE timely_response IS NOT NULL AND timely_response NOT IN ('Yes','No')").fetchone()[0]
        add("timely response source categories",invalid_yes_no==0,f"unexpected values={invalid_yes_no:,}")
        python_year={}
        for p in parts:
            d=pd.read_parquet(p,columns=["year"]); vals=d.year.dropna().astype(int).value_counts()
            for y,n in vals.items():python_year[int(y)]=python_year.get(int(y),0)+int(n)
        sql_year=dict(con.execute("SELECT year,COUNT(*) FROM fact_complaints WHERE year IS NOT NULL GROUP BY year"))
        add("Python-to-SQL yearly aggregate reconciliation",python_year==sql_year,f"years checked={len(python_year)}")
    finally: con.close()
    fact_export=ROOT/"data/powerbi/fact_complaints.parquet"
    export_rows=pq.ParquetFile(fact_export).metadata.num_rows if fact_export.exists() else -1
    add("Power BI fact export reconciliation",export_rows==fact,f"database={fact:,}; export={export_rows:,}")
    add("official raw inputs present",RAW_CSV.exists() and RAW_ARCHIVE.exists(),f"archive={RAW_ARCHIVE.exists()}; extracted csv={RAW_CSV.exists()}")
    result={"status":"PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL","checks":checks,"raw_csv_bytes":RAW_CSV.stat().st_size if RAW_CSV.exists() else None,"clean_rows":clean,"database_rows":fact,"powerbi_fact_rows":export_rows}
    report="Validation status: "+result["status"]+"\n\n"+"\n".join(f"{x['status']}: {x['check']} — {x['detail']}" for x in checks)+"\n"
    (ROOT/"outputs/reports/validation_report.txt").write_text(report,encoding="utf-8")
    (ROOT/"outputs/reports/validation_report.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    if result["status"]!="PASS": raise RuntimeError("Critical validation failed; see outputs/reports/validation_report.txt")
    return result
