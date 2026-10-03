"""Export full fact and dimensions in Power BI-friendly formats."""
from __future__ import annotations
import csv, sqlite3
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from .config import DB_PATH, ROOT

def export_powerbi(db_path:Path=DB_PATH)->dict:
    out=ROOT/"data/powerbi"; out.mkdir(parents=True,exist_ok=True); con=sqlite3.connect(db_path)
    dimensions={"dim_date":"SELECT * FROM dim_date ORDER BY date_key","dim_company":"SELECT * FROM dim_company ORDER BY company_id",
                "dim_product":"SELECT * FROM dim_product ORDER BY product_id","dim_issue":"SELECT * FROM dim_issue ORDER BY issue_id",
                "dim_geography":"SELECT * FROM dim_geography ORDER BY state_id","dim_channel":"SELECT * FROM dim_channel ORDER BY channel_id"}
    dim_counts={}
    for name,query in dimensions.items():
        df=pd.read_sql_query(query,con); df.to_csv(out/f"{name}.csv",index=False,encoding="utf-8-sig"); dim_counts[name]=len(df)
    cursor=con.execute("SELECT * FROM fact_complaints"); names=[x[0] for x in cursor.description]
    numeric={"date_key","company_id","product_id","issue_id","state_id","channel_id","year","quarter","month","week","response_days","timely_response_flag","has_narrative","narrative_length","narrative_word_count"}
    schema=pa.schema([pa.field(col,pa.int64() if col in numeric else pa.string()) for col in names])
    target=out/"fact_complaints.parquet"; writer=pq.ParquetWriter(target,schema,compression="zstd")
    n=0
    try:
        while batch:=cursor.fetchmany(50_000):
            table=pa.Table.from_pylist([dict(zip(names,row)) for row in batch],schema=schema); writer.write_table(table); n+=len(batch)
    finally: writer.close(); con.close()
    # A local SQLite copy is an alternative when Parquet support is unavailable in a Power BI environment.
    (out/"README.md").write_text("""# Power BI data exports\n\nImport `fact_complaints.parquet` with **Get data → Parquet**. Import each `dim_*.csv` through **Text/CSV**. Keep all rows; these are full-data exports. In Power Query, set `date_received` and `date_sent_to_company` to Date, complaint and ZIP identifiers to Text, and metric/foreign-key fields to Whole number. Relate integer keys as documented in `../../powerbi/POWER_BI_MODEL.md`. `complaints.db` in the repository's database folder is also available for SQLite-capable connectors.\n\nThe narrative column contains the CFPB public narrative text when consumers consented. Handle it as consumer-provided text and retain the published data cautions.\n""",encoding="utf-8")
    return {"fact_rows":n,"fact_size_bytes":target.stat().st_size,"dimensions":dim_counts,"folder":str(out)}
