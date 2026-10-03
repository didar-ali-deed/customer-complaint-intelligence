"""Run the complete official-source complaint analytics pipeline."""
from __future__ import annotations
import json, logging, time
import argparse
from pathlib import Path
from .config import ROOT
from .download_data import download_data
from .inspect_data import profile_raw
from .clean_data import clean_data
from .feature_engineering import engineer_features
from .build_database import build_database
from .sql_analysis import run_sql_analyses
from .eda import create_visualizations
from .narrative_analysis import analyze_narratives
from .export_powerbi import export_powerbi
from .validate_outputs import validate_outputs
from .publish_reports import publish_reports

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume-from",choices=["profile","cleaning","features","database","sql","visualizations","narratives","powerbi","validation"],help="Resume from an existing completed pipeline stage")
    resume_from=parser.parse_args().resume_from
    logdir=ROOT/"outputs/logs"; logdir.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.FileHandler(logdir/"pipeline.log",encoding="utf-8"),logging.StreamHandler()])
    started=time.time(); results={}
    stages=[("download",download_data),("raw_profile",profile_raw),("cleaning",clean_data),
                      ("features",engineer_features),("database",build_database),("sql",run_sql_analyses),
                      ("visualizations",create_visualizations),("narratives",analyze_narratives),
                      ("powerbi",export_powerbi),("validation",validate_outputs)]
    if resume_from:
        start=next(i for i,(name,_) in enumerate(stages) if name==resume_from)
        stages=stages[start:]
    for name,func in stages:
        logging.info("Starting %s",name); results[name]=func(); logging.info("Completed %s",name)
    results["runtime_seconds"]=round(time.time()-started,1)
    publish_reports(results)
    (ROOT/"outputs/reports/pipeline_run.json").write_text(json.dumps(results,indent=2,default=str),encoding="utf-8")
    logging.info("Pipeline complete in %.1f seconds",results["runtime_seconds"])

if __name__=="__main__": main()
