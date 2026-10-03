"""Create legible, reproducible PNG visuals from SQL aggregates."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .config import DB_PATH, ROOT

def create_visualizations(db_path:Path=DB_PATH)->dict:
    out=ROOT/"outputs/figures"; out.mkdir(parents=True,exist_ok=True); con=sqlite3.connect(db_path)
    queries={
      "complaint_trend_over_time":("SELECT year_month,COUNT(*) n FROM fact_complaints GROUP BY 1 ORDER BY 1","line","year_month","n","Monthly complaints received"),
      "complaints_by_product":("SELECT p.product,COUNT(*) n FROM fact_complaints f JOIN dim_product p USING(product_id) GROUP BY 1 ORDER BY n DESC LIMIT 12","barh","product","n","Complaints by product (top 12)"),
      "complaints_by_issue":("SELECT i.issue,COUNT(*) n FROM fact_complaints f JOIN dim_issue i USING(issue_id) GROUP BY 1 ORDER BY n DESC LIMIT 12","barh","issue","n","Complaints by issue (top 12)"),
      "complaints_by_company":("SELECT c.company,COUNT(*) n FROM fact_complaints f JOIN dim_company c USING(company_id) GROUP BY 1 ORDER BY n DESC LIMIT 12","barh","company","n","Complaints by company (top 12)"),
      "timely_response_trend":("SELECT year_month,AVG(timely_response_flag)*100 pct FROM fact_complaints WHERE timely_response_flag IS NOT NULL GROUP BY 1 ORDER BY 1","line","year_month","pct","Timely responses over time (%)"),
      "company_response_distribution":("SELECT COALESCE(company_response_to_consumer,'Unknown') label,COUNT(*) n FROM fact_complaints GROUP BY 1 ORDER BY n DESC","barh","label","n","Company response to consumer"),
      "complaints_by_state":("SELECT g.state,COUNT(*) n FROM fact_complaints f JOIN dim_geography g USING(state_id) GROUP BY 1 ORDER BY n DESC LIMIT 20","barh","state","n","Complaints by state (top 20)"),
      "submission_channel_distribution":("SELECT ch.submitted_via label,COUNT(*) n FROM fact_complaints f JOIN dim_channel ch USING(channel_id) GROUP BY 1 ORDER BY n DESC","barh","label","n","Complaints by submission channel"),
      "year_over_year_growth":("WITH y AS(SELECT year,COUNT(*) n FROM fact_complaints GROUP BY 1) SELECT year,100.0*(n-LAG(n) OVER(ORDER BY year))/NULLIF(LAG(n) OVER(ORDER BY year),0) pct FROM y ORDER BY year","bar","year","pct","Year-over-year complaint growth (%)"),
      "narrative_availability":("SELECT year,100.0*AVG(has_narrative) pct FROM fact_complaints GROUP BY 1 ORDER BY 1","line","year","pct","Complaints with narratives (%)"),
      "rolling_12_month_trend":("WITH m AS(SELECT year_month,COUNT(*) n FROM fact_complaints GROUP BY 1) SELECT year_month,SUM(n) OVER(ORDER BY year_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) rolling FROM m ORDER BY year_month","line","year_month","rolling","Rolling 12-month complaints"),
      "emerging_issues":("WITH y AS(SELECT i.issue,f.year,COUNT(*) n FROM fact_complaints f JOIN dim_issue i USING(issue_id) GROUP BY 1,2), z AS(SELECT *,LAG(n) OVER(PARTITION BY issue ORDER BY year) prev FROM y) SELECT issue||' ('||year||')' label,100.0*(n-prev)/NULLIF(prev,0) pct FROM z WHERE prev>=100 ORDER BY year DESC,pct DESC LIMIT 15","barh","label","pct","Largest issue growth rates (prior-year base ≥100)")}
    paths=[]
    plt.rcParams.update({"figure.dpi":140,"savefig.dpi":220,"axes.spines.top":False,"axes.spines.right":False,"font.size":9})
    for name,(sql,kind,x,y,title) in queries.items():
        df=pd.read_sql_query(sql,con)
        if df.empty: continue
        if kind=="line":
            fig,ax=plt.subplots(figsize=(12,4)); ax.plot(df[x],df[y],color="#146C94",linewidth=1.8); ax.tick_params(axis="x",rotation=55)
        elif kind=="barh":
            df=df.sort_values(y); fig,ax=plt.subplots(figsize=(10,max(4,.32*len(df)))); ax.barh(df[x].astype(str),df[y],color="#19A7CE"); ax.set_xlabel("Percent" if "pct" in y else "Complaints")
        else:
            fig,ax=plt.subplots(figsize=(10,4)); ax.bar(df[x].astype(str),df[y],color="#19A7CE"); ax.tick_params(axis="x",rotation=30)
        ax.set_title(title,loc="left",weight="bold"); ax.set_ylabel(y.replace("_"," ").title()); ax.grid(axis="x" if kind=="barh" else "y",alpha=.2)
        fig.tight_layout(); path=out/f"{name}.png"; fig.savefig(path,bbox_inches="tight"); plt.close(fig); paths.append(str(path.relative_to(ROOT)))
    con.close()
    return {"count":len(paths),"files":paths}
