"""Stream raw CFPB records through deterministic, documented cleaning rules."""
from __future__ import annotations
import logging, re, shutil
from pathlib import Path
import pandas as pd
from .config import RAW_CSV, CLEAN_DIR, CHUNK_SIZE

LOG = logging.getLogger(__name__)
DATE_MAP = {"Date received":"date_received", "Date sent to company":"date_sent_to_company"}
YES_NO = {"yes":"Yes", "no":"No"}

def snake_case(label: str) -> str:
    value = label.strip().lower().replace("?", "")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

def clean_data(path: Path = RAW_CSV, output_dir: Path = CLEAN_DIR) -> dict:
    """Clean in chunks after profiling; retain source columns and valid narratives."""
    if output_dir.exists(): shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    total = kept = invalid_id = duplicate_id = invalid_dates = 0
    seen_ids: set[str] = set()
    for part, chunk in enumerate(pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=CHUNK_SIZE, low_memory=False), 1):
        total += len(chunk)
        chunk.columns = [snake_case(c) for c in chunk.columns]
        for col in chunk.columns:
            chunk[col] = chunk[col].astype("string").str.strip()
            chunk[col] = chunk[col].mask(chunk[col] == "", pd.NA)
        for col in ("timely_response", "consumer_disputed", "consumer_consent_provided"):
            if col in chunk:
                normalized = chunk[col].str.casefold().map(YES_NO)
                chunk[col] = normalized.fillna(chunk[col])
        if "state" in chunk:
            chunk["state"] = chunk.state.str.upper().str.strip()
            chunk.loc[~chunk.state.str.fullmatch(r"[A-Z]{2}", na=False), "state"] = pd.NA
        for col in DATE_MAP.values():
            if col in chunk:
                raw_nonnull = chunk[col].notna()
                chunk[col] = pd.to_datetime(chunk[col], errors="coerce").dt.strftime("%Y-%m-%d")
                invalid_dates += int((raw_nonnull & chunk[col].isna()).sum())
        # Keep ZIP values as strings, including leading zeroes; narratives are only trimmed.
        id_col = "complaint_id"
        if id_col in chunk:
            valid = chunk[id_col].notna() & chunk[id_col].str.fullmatch(r"\d+", na=False)
            invalid_id += int((~valid).sum())
            chunk = chunk.loc[valid]
            # Series.isin(set) materializes the whole Python set on every chunk; map
            # performs bounded per-ID membership checks without an expanding copy.
            duplicate_mask = chunk[id_col].map(seen_ids.__contains__) | chunk[id_col].duplicated(keep="first")
            duplicate_id += int(duplicate_mask.sum())
            seen_ids.update(chunk.loc[~duplicate_mask, id_col].dropna().tolist())
            chunk = chunk.loc[~duplicate_mask]
        kept += len(chunk)
        chunk.to_parquet(output_dir/f"part-{part:05d}.parquet", index=False, engine="pyarrow", compression="snappy")
    result = {"raw_rows":total,"clean_rows":kept,"invalid_complaint_ids_removed":invalid_id,
              "duplicate_complaint_ids_removed":duplicate_id,"malformed_dates_coerced_to_null":invalid_dates,
              "parts":part,"transformations":["column names converted to snake_case","surrounding whitespace trimmed","empty strings converted to null","yes/no response fields case-normalized","state abbreviations uppercased and non-state codes nulled","date fields parsed and malformed values nulled","invalid complaint IDs and duplicate IDs removed","ZIP codes retained as strings","narrative text retained with surrounding whitespace removed"]}
    LOG.info("Cleaned %s -> %s rows", total, kept)
    return result
