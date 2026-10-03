"""Build indexed SQLite star schema from feature parquet parts."""
from __future__ import annotations
import logging, sqlite3
from pathlib import Path
import pandas as pd
from .config import CLEAN_DIR, DB_PATH

LOG=logging.getLogger(__name__)
STAGE_COLUMNS=["complaint_id","date_received","date_sent_to_company","product","sub_product","issue","sub_issue","company_public_response","company","state","zip_code","tags","consumer_consent_provided","submitted_via","company_response_to_consumer","timely_response","consumer_disputed","consumer_complaint_narrative","year","quarter","month","month_name","year_month","week","day_of_week","response_days","timely_response_flag","has_narrative","narrative_length","narrative_word_count"]

def build_database(directory: Path=CLEAN_DIR, db_path: Path=DB_PATH) -> dict:
    """Load clean parts to staging, construct dimensions/fact, then add indexes."""
    db_path.parent.mkdir(parents=True,exist_ok=True); db_path.unlink(missing_ok=True)
    con=sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA journal_mode=WAL"); con.execute("PRAGMA synchronous=NORMAL"); con.execute("PRAGMA temp_store=MEMORY")
        first=True; rows=0
        for part in sorted(directory.glob("part-*.parquet")):
            available=pd.read_parquet(part).columns
            frame=pd.read_parquet(part,columns=[c for c in STAGE_COLUMNS if c in available])
            for column in STAGE_COLUMNS:
                if column not in frame: frame[column]=pd.NA
            frame=frame[STAGE_COLUMNS]
            frame.to_sql("staging",con,if_exists="replace" if first else "append",index=False,chunksize=10000); first=False; rows+=len(frame)
        con.executescript((Path(__file__).resolve().parents[1]/"sql/01_schema.sql").read_text(encoding="utf-8"))
        # Dimension keys are compact integer surrogates, assigned in stable alphabetical order.
        dimensions={"company":("dim_company","company_id","company"),"product":("dim_product","product_id","product"),
                    "issue":("dim_issue","issue_id","issue"),"state":("dim_geography","state_id","state"),
                    "submitted_via":("dim_channel","channel_id","submitted_via")}
        for source,(table,key,col) in dimensions.items():
            con.execute(f"INSERT INTO {table}({col}) SELECT DISTINCT {source} FROM staging WHERE {source} IS NOT NULL ORDER BY {source}")
        con.execute("""WITH RECURSIVE calendar(d) AS (
        SELECT MIN(date_received) FROM staging WHERE date_received IS NOT NULL
        UNION ALL SELECT date(d,'+1 day') FROM calendar WHERE d < (SELECT MAX(date_received) FROM staging WHERE date_received IS NOT NULL)
        ) INSERT INTO dim_date(date_key,date,year,quarter,month,month_name,year_month,week,day_of_week,day_of_week_sort)
        SELECT CAST(REPLACE(d,'-','') AS INTEGER),d,CAST(strftime('%Y',d) AS INTEGER),
        CAST((CAST(strftime('%m',d) AS INTEGER)+2)/3 AS INTEGER),CAST(strftime('%m',d) AS INTEGER),
        CASE strftime('%m',d) WHEN '01' THEN 'January' WHEN '02' THEN 'February' WHEN '03' THEN 'March' WHEN '04' THEN 'April' WHEN '05' THEN 'May' WHEN '06' THEN 'June' WHEN '07' THEN 'July' WHEN '08' THEN 'August' WHEN '09' THEN 'September' WHEN '10' THEN 'October' WHEN '11' THEN 'November' WHEN '12' THEN 'December' END,
        strftime('%Y-%m',d),CAST(strftime('%W',d) AS INTEGER),
        CASE strftime('%w',d) WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday' WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday' ELSE 'Saturday' END,
        CASE strftime('%w',d) WHEN '0' THEN 7 ELSE CAST(strftime('%w',d) AS INTEGER) END FROM calendar""")
        con.execute("""INSERT INTO fact_complaints
        SELECT s.complaint_id, CAST(REPLACE(s.date_received,'-','') AS INTEGER), c.company_id,p.product_id,i.issue_id,g.state_id,ch.channel_id,
        s.date_received,s.date_sent_to_company,s.sub_product,s.sub_issue,s.zip_code,s.tags,s.consumer_consent_provided,
        s.company_public_response,s.company_response_to_consumer,s.timely_response,s.consumer_disputed,s.consumer_complaint_narrative,
        s.year,s.quarter,s.month,s.month_name,s.year_month,s.week,s.day_of_week,s.response_days,s.timely_response_flag,
        s.has_narrative,s.narrative_length,s.narrative_word_count
        FROM staging s LEFT JOIN dim_company c ON s.company=c.company LEFT JOIN dim_product p ON s.product=p.product
        LEFT JOIN dim_issue i ON s.issue=i.issue LEFT JOIN dim_geography g ON s.state=g.state
        LEFT JOIN dim_channel ch ON s.submitted_via=ch.submitted_via""")
        con.execute("DROP TABLE staging")
        con.executescript((Path(__file__).resolve().parents[1]/"sql/02_indexes.sql").read_text(encoding="utf-8"))
        con.commit()
        counts={table:con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ["fact_complaints",* [v[0] for v in dimensions.values()],"dim_date"]}
        return {"counts":counts,"db_path":str(db_path),"db_size_bytes":db_path.stat().st_size}
    finally:
        con.close()
