"""Practical, reproducible TF-IDF and NMF analysis of available narratives."""
from __future__ import annotations
import json, re, sqlite3
from pathlib import Path
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from .config import DB_PATH, ROOT, NLP_MAX_DOCUMENTS

class _Median:
    def __init__(self): self.values=[]
    def step(self,value):
        if value is not None:self.values.append(value)
    def finalize(self):
        if not self.values:return None
        self.values.sort(); n=len(self.values); i=n//2
        return self.values[i] if n%2 else (self.values[i-1]+self.values[i])/2

def analyze_narratives(db_path:Path=DB_PATH)->dict:
    """Analyze consumer narratives when published; otherwise published company responses."""
    out=ROOT/"outputs/tables"; out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(db_path)
    try:
        con.create_aggregate("MEDIAN",1,_Median)
        narrative_total=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE has_narrative=1").fetchone()[0]
        if narrative_total:
            text_column="consumer_complaint_narrative"; source_label="consumer complaint narratives"
            predicate="consumer_complaint_narrative IS NOT NULL AND consumer_complaint_narrative<>''"
        else:
            text_column="company_public_response"; source_label="CFPB-published company public responses (consumer complaint narratives absent from this CFPB release)"
            predicate="company_public_response IS NOT NULL AND company_public_response<>''"
        total=con.execute(f"SELECT COUNT(*) FROM fact_complaints WHERE {predicate}").fetchone()[0]
        docs=pd.read_sql_query(f"SELECT f.{text_column} narrative,p.product,i.issue,c.company FROM fact_complaints f LEFT JOIN dim_product p USING(product_id) LEFT JOIN dim_issue i USING(issue_id) LEFT JOIN dim_company c USING(company_id) WHERE f.{predicate} ORDER BY f.complaint_id LIMIT {NLP_MAX_DOCUMENTS}",con)
        lengths=pd.read_sql_query(f"SELECT year,AVG(LENGTH({text_column})) mean_chars,AVG(LENGTH({text_column})-LENGTH(REPLACE({text_column},' ',''))+1) mean_words,MEDIAN(LENGTH({text_column})) median_chars FROM fact_complaints WHERE {predicate} GROUP BY year ORDER BY year",con)
    finally: con.close()
    lengths.to_csv(out/"narrative_length_by_year.csv",index=False)
    def normalize(text:str)->str:
        return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9']+"," ",str(text).lower())).strip()
    docs["clean_text"]=docs.narrative.map(normalize)
    docs=docs.loc[docs.clean_text.str.len()>0].reset_index(drop=True)
    stop=set(ENGLISH_STOP_WORDS)|{"said","told","company","account","would","could","also","one","get","got","back","please"," CFPB".strip().lower()}
    vector=TfidfVectorizer(stop_words=sorted(stop),ngram_range=(1,2),min_df=5,max_features=5000,sublinear_tf=True,token_pattern=r"(?u)\b[a-z][a-z']{2,}\b")
    matrix=vector.fit_transform(docs.clean_text); terms=vector.get_feature_names_out()
    import numpy as np
    sums=np.asarray(matrix.sum(axis=0)).ravel(); top=np.argsort(sums)[::-1][:100]
    pd.DataFrame({"term":terms[top],"tfidf_weight":sums[top]}).to_csv(out/"narrative_top_terms.csv",index=False)
    # Top terms for the most common products and issue groups with enough narratives.
    subset=[]
    for field in ["product","issue","company"]:
        groups=docs[field].value_counts()
        groups=groups[groups>=100].head(12)
        for label,count in groups.items():
            mask=docs[field].eq(label).to_numpy()
            subset.append({"group_type":field,"group":label,"narratives":int(count),"top_terms":"; ".join(terms[np.argsort(np.asarray(matrix[mask].sum(axis=0)).ravel())[::-1][:10]])})
    pd.DataFrame(subset).to_csv(out/"narrative_terms_by_segment.csv",index=False)
    topic_n=min(len(docs),30_000)
    topic_matrix=matrix[:topic_n]
    model=NMF(n_components=min(8,max(1,matrix.shape[0]-1),max(1,matrix.shape[1]-1)),init="nndsvda",random_state=42,max_iter=200)
    weights=model.fit_transform(topic_matrix)
    topics=[]
    for i,component in enumerate(model.components_):
        inds=np.argsort(component)[::-1][:12]
        topics.append({"topic_id":i+1,"terms":"; ".join(terms[inds]),"documents_assigned":int((weights.argmax(axis=1)==i).sum()),"corpus_documents":topic_n})
    topic_df=pd.DataFrame(topics); topic_df.to_csv(out/"narrative_topics.csv",index=False)
    result={"text_source":source_label,"consumer_narratives_available":int(narrative_total),"text_records_available":int(total),"documents_analyzed":len(docs),"corpus_cap":NLP_MAX_DOCUMENTS,
            "method":"Deterministic first N complaint IDs; TF-IDF unigrams/bigrams on the corpus and 8-component NMF on its first 30,000 documents; English stopword list plus project stopwords.",
            "caution":"Themes are algorithmic groupings for investigation, not objective consumer sentiment or causal findings."}
    (ROOT/"outputs/reports/narrative_analysis_metadata.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
