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
    """Analyze a deterministic capped corpus; never imply it is all narrative text."""
    out=ROOT/"outputs/tables"; out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(db_path)
    try:
        con.create_aggregate("MEDIAN",1,_Median)
        total=con.execute("SELECT COUNT(*) FROM fact_complaints WHERE has_narrative=1").fetchone()[0]
        docs=pd.read_sql_query(f"SELECT consumer_complaint_narrative narrative,product,issue,company FROM fact_complaints WHERE has_narrative=1 ORDER BY complaint_id LIMIT {NLP_MAX_DOCUMENTS}",con)
        lengths=pd.read_sql_query("SELECT year,AVG(narrative_length) mean_chars,AVG(narrative_word_count) mean_words,MEDIAN(narrative_length) median_chars FROM fact_complaints WHERE has_narrative=1 GROUP BY year ORDER BY year",con)
    finally: con.close()
    lengths.to_csv(out/"narrative_length_by_year.csv",index=False)
    def normalize(text:str)->str:
        return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9']+"," ",str(text).lower())).strip()
    docs["clean_text"]=docs.narrative.map(normalize)
    docs=docs.loc[docs.clean_text.str.len()>0].reset_index(drop=True)
    stop=set(ENGLISH_STOP_WORDS)|{"said","told","company","account","would","could","also","one","get","got","back","please"," CFPB".strip().lower()}
    vector=TfidfVectorizer(stop_words=stop,ngram_range=(1,2),min_df=5,max_features=5000,sublinear_tf=True,token_pattern=r"(?u)\b[a-z][a-z']{2,}\b")
    matrix=vector.fit_transform(docs.clean_text); terms=vector.get_feature_names_out()
    import numpy as np
    sums=np.asarray(matrix.sum(axis=0)).ravel(); top=np.argsort(sums)[::-1][:100]
    pd.DataFrame({"term":terms[top],"tfidf_weight":sums[top]}).to_csv(out/"narrative_top_terms.csv",index=False)
    # Top terms for the most common products and issue groups with enough narratives.
    subset=[]
    for field in ["product","issue"]:
        for label,count in docs[field].value_counts().head(12).items():
            subset.append({"group_type":field,"group":label,"narratives":int(count),"top_terms":"; ".join(terms[np.argsort(np.asarray(matrix[docs[field].eq(label)].sum(axis=0)).ravel())[::-1][:10]])})
    pd.DataFrame(subset).to_csv(out/"narrative_terms_by_segment.csv",index=False)
    topic_n=min(len(docs),30_000)
    topic_matrix=matrix[:topic_n]
    model=NMF(n_components=8,init="nndsvda",random_state=42,max_iter=200)
    weights=model.fit_transform(topic_matrix)
    topics=[]
    for i,component in enumerate(model.components_):
        inds=np.argsort(component)[::-1][:12]
        topics.append({"topic_id":i+1,"terms":"; ".join(terms[inds]),"documents_assigned":int((weights.argmax(axis=1)==i).sum()),"corpus_documents":topic_n})
    topic_df=pd.DataFrame(topics); topic_df.to_csv(out/"narrative_topics.csv",index=False)
    result={"narratives_available":int(total),"documents_analyzed":len(docs),"corpus_cap":NLP_MAX_DOCUMENTS,
            "method":"Deterministic first N complaint IDs; TF-IDF unigrams/bigrams on the corpus and 8-component NMF on its first 30,000 documents; English stopword list plus project stopwords.",
            "caution":"Themes are algorithmic groupings for investigation, not objective consumer sentiment or causal findings."}
    (ROOT/"outputs/reports/narrative_analysis_metadata.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
