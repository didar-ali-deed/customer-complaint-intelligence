"""Add complaint-level time, response, narrative, and dashboard fields."""
from __future__ import annotations
import logging, shutil
from pathlib import Path
import pandas as pd
from .config import CLEAN_DIR

LOG=logging.getLogger(__name__)

def engineer_features(directory: Path = CLEAN_DIR) -> dict:
    """Replace clean parquet parts with feature-enriched parts; return row totals."""
    import tempfile
    temp=Path(tempfile.mkdtemp(prefix="feature_parts_", dir=directory.parent))
    total=0
    for source in sorted(directory.glob("part-*.parquet")):
        df=pd.read_parquet(source)
        received=pd.to_datetime(df["date_received"],errors="coerce")
        sent=pd.to_datetime(df.get("date_sent_to_company"),errors="coerce")
        df["date_received_date"]=received.dt.strftime("%Y-%m-%d")
        df["date_sent_to_company_date"]=sent.dt.strftime("%Y-%m-%d")
        df["year"]=received.dt.year.astype("Int16"); df["quarter"]=received.dt.quarter.astype("Int8")
        df["month"]=received.dt.month.astype("Int8"); df["month_name"]=received.dt.month_name()
        df["year_month"]=received.dt.strftime("%Y-%m")
        df["week"]=received.dt.isocalendar().week.astype("Int8")
        df["day_of_week"]=received.dt.day_name()
        df["response_days"]=(sent-received).dt.days.astype("Int32")
        df.loc[df.response_days<0,"response_days"]=pd.NA
        timely=df.get("timely_response",pd.Series(pd.NA,index=df.index)).str.casefold().map({"yes":1,"no":0})
        df["timely_response_flag"]=timely.astype("Int8")
        narrative=df.get("consumer_complaint_narrative",pd.Series(pd.NA,index=df.index)).fillna("")
        df["has_narrative"]=(narrative.str.len()>0).astype("Int8")
        df["narrative_length"]=narrative.str.len().astype("Int32")
        df["narrative_word_count"]=narrative.str.split().str.len().fillna(0).astype("Int32")
        df["company_response_group"]=df.get("company_response_to_consumer",pd.Series(pd.NA,index=df.index)).fillna("Unknown")
        df["submission_channel_group"]=df.get("submitted_via",pd.Series(pd.NA,index=df.index)).fillna("Unknown")
        df["product_group"]=df.get("product",pd.Series(pd.NA,index=df.index)).fillna("Unknown")
        df.to_parquet(temp/source.name,index=False,engine="pyarrow",compression="snappy"); total+=len(df)
    shutil.rmtree(directory)
    temp.replace(directory)
    LOG.info("Engineered features for %s rows",total)
    return {"feature_rows":total,"feature_columns":["year","quarter","month","month_name","year_month","week","day_of_week","response_days","timely_response_flag","has_narrative","narrative_length","narrative_word_count","company_response_group","submission_channel_group","product_group"]}
