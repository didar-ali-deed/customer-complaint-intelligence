"""Profile the complete raw CSV in chunks before any cleaning occurs."""
from __future__ import annotations
import json, logging
from collections import Counter
from pathlib import Path
import pandas as pd
from .config import ROOT, RAW_CSV, PROFILE_CSV, PROFILE_JSON, CHUNK_SIZE

LOG = logging.getLogger(__name__)
DATE_COLUMNS = {"Date received", "Date sent to company"}

def write_human_report(result:dict)->Path:
    """Render a concise quality summary from a completed machine-readable profile."""
    profile=pd.read_csv(PROFILE_CSV)
    absent=[name for name in ["Consumer complaint narrative","Consumer consent provided?","Consumer disputed?"] if name not in result["column_names"]]
    nonzero_whitespace={k:v for k,v in result["whitespace_edge_rows_by_column"].items() if v}
    nonzero_case={k:v for k,v in result["case_variant_groups_by_column"].items() if v}
    nonzero_missing=profile.loc[profile.missing_count>0,["column","missing_count","missing_pct"]]
    text_stats=result.get("text_statistics",{})
    lines=["# Raw Data Quality Report","",f"- Rows: {result['rows']:,}",f"- Columns: {result['columns']}",
           "- Raw parser dtypes: all string values to preserve identifiers and ZIP codes.",
           f"- Estimated cumulative parsed memory across 100,000-row chunks: {result['estimated_cumulative_chunk_memory_bytes']:,} bytes (not peak memory).",
           f"- Duplicate complaint IDs found within chunks: {result['duplicate_complaint_ids_within_chunks']:,}",
           f"- Exact duplicate rows found across the streamed source: {result['exact_duplicates_detected_across_stream']:,}",
           f"- Invalid state-code rows before cleaning: {result['invalid_state_rows']:,}",
           f"- Unexpected values in available yes/no fields: {sum(result['unexpected_yes_no_values_by_field'].values()):,}",
           f"- Non-two-letter states are normalized to null during cleaning; valid complaint rows are retained.",
           f"- Date ranges: `{json.dumps(result['date_ranges'])}`",
           f"- Malformed dates: `{json.dumps(result['malformed_dates'])}`",
           f"- CFPB expected fields absent from this release: {', '.join(absent) if absent else 'none'}.",
           f"- Whitespace anomalies by column: `{json.dumps(nonzero_whitespace)}`",
           f"- Case-only variant groups in audited categories: `{json.dumps(nonzero_case)}`",
           f"- Available text-field measurements: `{json.dumps(text_stats)}`","",
           "## Missing values","",(nonzero_missing.to_string(index=False) if len(nonzero_missing) else "No missing values detected."),"",
           "## Column profile","","See `outputs/reports/raw_data_profile.csv` for each field's raw type, missing count and percentage, exact/estimated cardinality, whitespace count, category case-variant groups, and example values.","",
           "## Profiling notes","","Profiling completes before cleaning. Low-cardinality counts are exact; high-cardinality counts use bounded-memory HyperLogLog estimates (p=12). Exact row fingerprints are compared across streamed records. The raw CSV is preserved unchanged; missing source fields are not inferred or fabricated.",""]
    path=ROOT/"docs/DATA_QUALITY_REPORT.md"; path.write_text("\n".join(lines),encoding="utf-8"); return path

class Cardinality:
    """Exact low cardinality, then bounded-memory HyperLogLog estimate."""
    def __init__(self,limit:int=50_000,p:int=12):
        self.limit=limit; self.p=p; self.exact=set(); self.registers=None
    def add(self,value:str)->None:
        if self.registers is None:
            self.exact.add(value)
            if len(self.exact)>self.limit:
                self.registers=[0]*(1<<self.p)
                old=self.exact; self.exact=None
                for item in old:self._add_hash(hash(item)&((1<<64)-1))
        else:self._add_hash(hash(value)&((1<<64)-1))
    def _add_hash(self,h:int)->None:
        index=h&((1<<self.p)-1); w=h>>self.p
        rank=(64-self.p)-w.bit_length()+1
        self.registers[index]=max(self.registers[index],rank)
    def count(self)->int:
        if self.registers is None:return len(self.exact)
        m=len(self.registers); estimate=.7213/(1+1.079/m)*m*m/sum(2.0**(-r) for r in self.registers)
        zeros=self.registers.count(0)
        if estimate<=2.5*m and zeros: estimate=m*__import__('math').log(m/zeros)
        return round(estimate)

def profile_raw(path: Path = RAW_CSV) -> dict:
    """Collect schema, null, cardinality, duplicate, date, and text diagnostics."""
    counts, missing, uniques, dtypes, examples = Counter(), Counter(), {}, {}, {}
    whitespace=Counter(); invalid_states=0; invalid_flags=Counter(); case_forms={}; memory_bytes=0
    date_min, date_max, malformed = {}, {}, Counter()
    text_stats = Counter(); duplicate_ids = 0; exact_fingerprints = set(); exact_duplicates = 0
    rows = 0
    for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=CHUNK_SIZE, low_memory=False):
        rows += len(chunk)
        memory_bytes += int(chunk.memory_usage(index=True,deep=True).sum())
        for col in chunk.columns:
            dtypes.setdefault(col, "string")
            s = chunk[col].str.strip()
            whitespace[col] += int((chunk[col] != s).sum())
            missing[col] += int((s == "").sum())
            tracker=uniques.setdefault(col,Cardinality())
            vals = s[s != ""].unique()
            for value in vals: tracker.add(value)
            if col in {"Product","Sub-product","Issue","Sub-issue","Submitted via","Company public response"}:
                forms=case_forms.setdefault(col,{})
                for value in vals:
                    forms.setdefault(value.casefold(),set()).add(value)
            if len(examples.get(col, [])) < 12:
                examples[col] = list(dict.fromkeys(examples.get(col, []) + list(vals)[:12]))[:12]
            if "narrative" in col.lower() or "response" in col.lower():
                lengths = s[s != ""].str.len()
                text_stats[col+"_nonempty"] += int(len(lengths)); text_stats[col+"_characters"] += int(lengths.sum())
        for col in DATE_COLUMNS & set(chunk.columns):
            parsed = pd.to_datetime(chunk[col], errors="coerce")
            malformed[col] += int(((chunk[col] != "") & parsed.isna()).sum())
            if parsed.notna().any():
                lo, hi = parsed.min().isoformat(), parsed.max().isoformat()
                date_min[col] = min(date_min.get(col, lo), lo); date_max[col] = max(date_max.get(col, hi), hi)
        if "State" in chunk:
            state=chunk["State"].str.strip()
            invalid_states += int(((state!="") & ~state.str.fullmatch(r"[A-Za-z]{2}",na=False)).sum())
        for flag in ("Timely response?","Consumer disputed?","Consumer consent provided?"):
            if flag in chunk:
                values=chunk[flag].str.strip().str.casefold()
                invalid_flags[flag] += int(((values!="") & ~values.isin(["yes","no"])).sum())
        if "Complaint ID" in chunk:
            ids = chunk["Complaint ID"].str.strip()
            duplicate_ids += int(ids.duplicated().sum())
        # Exact duplicate rate is derived from whole-row fingerprints; memory stays bounded.
        for row in chunk.itertuples(index=False, name=None):
            key = hash(tuple(row))
            if key in exact_fingerprints: exact_duplicates += 1
            exact_fingerprints.add(key)
    fields = []
    for col in missing:
        fields.append({"column": col, "dtype": dtypes[col], "missing_count": missing[col],
                       "missing_pct": round(100*missing[col]/rows, 4) if rows else 0,
                       "unique_nonempty": uniques[col].count(), "cardinality_method":"exact" if uniques[col].registers is None else "HyperLogLog estimate (p=12)",
                       "whitespace_edge_rows":whitespace[col],"case_variant_groups":sum(len(forms)>1 for forms in case_forms.get(col,{}).values()),
                       "sample_values": " | ".join(examples.get(col, []))})
    frame = pd.DataFrame(fields).sort_values("missing_pct", ascending=False)
    PROFILE_CSV.parent.mkdir(parents=True, exist_ok=True); frame.to_csv(PROFILE_CSV, index=False)
    result = {"rows": rows, "columns": len(fields), "column_names": [f["column"] for f in fields],
              "raw_parser_dtypes":"All CSV columns are ingested as pandas string values to preserve identifiers and ZIP leading zeroes.",
              "estimated_cumulative_chunk_memory_bytes":memory_bytes,
              "whitespace_edge_rows_by_column":dict(whitespace),
              "case_variant_groups_by_column":{col:sum(len(forms)>1 for forms in vals.values()) for col,vals in case_forms.items()},
              "invalid_state_rows":invalid_states,"unexpected_yes_no_values_by_field":dict(invalid_flags),
              "suspicious_category_samples":{field:examples.get(field,[]) for field in ["State","Timely response?","Consumer disputed?","Consumer consent provided?"] if field in examples},
              "duplicate_complaint_ids_within_chunks": duplicate_ids,
              "exact_duplicates_detected_across_stream": exact_duplicates,
              "date_ranges": {c:{"min":date_min.get(c),"max":date_max.get(c)} for c in DATE_COLUMNS if c in missing},
              "malformed_dates": dict(malformed), "text_statistics": dict(text_stats),
              "profile_csv": str(PROFILE_CSV), "top_missing": frame.head(20).to_dict(orient="records")}
    PROFILE_JSON.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    metadata_path=Path(__file__).resolve().parents[1]/"data/raw/source_metadata.json"
    if metadata_path.exists():
        metadata=json.loads(metadata_path.read_text(encoding="utf-8")); metadata["row_count"]=rows; metadata["column_count"]=len(fields)
        metadata_path.write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    write_human_report(result)
    LOG.info("Profiled %s rows and %s columns", rows, len(fields))
    return result

if __name__ == "__main__": print(json.dumps(profile_raw(), indent=2))
