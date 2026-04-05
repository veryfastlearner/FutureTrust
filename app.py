import sys, os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import io, re, json, traceback
import numpy as np
import requests
import pandas as pd
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _FAISS_OK = True
except ImportError:
    _FAISS_OK = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cos

try:
    from duckduckgo_search import DDGS
    _DDG_OK = True
except ImportError:
    _DDG_OK = False

try:
    import google.genai as genai
    _GENAI_OK = True
except ImportError:
    _GENAI_OK = False

st.set_page_config(page_title="FutureTrust · Misinformation Detector",page_icon="🛡️",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important}
.stApp{background:#05080f;background-image:radial-gradient(ellipse 80% 50% at 20% 0%,rgba(14,165,233,0.07) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 100%,rgba(99,102,241,0.06) 0%,transparent 60%);min-height:100vh}
section[data-testid="stSidebar"]{background:#080c15!important;border-right:1px solid #0f1e33!important}
section[data-testid="stSidebar"] *{color:#7a8fa6!important}
section[data-testid="stSidebar"] strong{color:#c8d8e8!important}
section[data-testid="stSidebar"] h4{color:#c8d8e8!important;font-size:.82rem!important;letter-spacing:.1em;text-transform:uppercase}
.hero{background:linear-gradient(135deg,#0a1628 0%,#071020 50%,#0c1830 100%);border:1px solid #112240;border-radius:24px;padding:3rem 3.5rem;margin-bottom:2rem;position:relative;overflow:hidden}
.hero::after{content:'';position:absolute;top:-80px;right:-80px;width:360px;height:360px;background:radial-gradient(circle,rgba(14,165,233,0.10) 0%,transparent 65%);border-radius:50%;pointer-events:none}
.hero-badge{display:inline-flex;align-items:center;gap:.4rem;background:rgba(14,165,233,0.1);border:1px solid rgba(14,165,233,0.25);border-radius:100px;padding:.25rem .85rem;font-size:.7rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:#38bdf8;margin-bottom:1rem}
.hero-title{font-family:'Syne',sans-serif;font-size:clamp(1.8rem,3vw,2.8rem);font-weight:800;color:#eef4ff;line-height:1.1;margin:0 0 .9rem}
.hero-title em{font-style:normal;color:#38bdf8}
.hero-sub{color:#4a6580;font-size:.93rem;line-height:1.65;max-width:540px}
.hero-chips{display:flex;gap:.45rem;flex-wrap:wrap;margin-top:1.4rem}
.chip{background:rgba(255,255,255,0.04);border:1px solid #112240;border-radius:8px;padding:.28rem .75rem;font-size:.73rem;font-weight:600;color:#4a6580}
.card{background:#080c15;border:1px solid #0f1e33;border-radius:18px;padding:1.6rem;margin-bottom:.9rem}
.card-tight{padding:1.1rem 1.4rem;margin-bottom:.65rem}
.verdict{border-radius:20px;padding:2.4rem 2rem;text-align:center;margin-bottom:1.2rem;position:relative;overflow:hidden}
.v-authentic{background:linear-gradient(135deg,rgba(16,185,129,.07),rgba(5,150,105,.03));border:1px solid rgba(16,185,129,.3);box-shadow:0 0 60px rgba(16,185,129,.07)}
.v-suspicious{background:linear-gradient(135deg,rgba(245,158,11,.07),rgba(217,119,6,.03));border:1px solid rgba(245,158,11,.3);box-shadow:0 0 60px rgba(245,158,11,.07)}
.v-misleading{background:linear-gradient(135deg,rgba(239,68,68,.07),rgba(185,28,28,.03));border:1px solid rgba(239,68,68,.3);box-shadow:0 0 60px rgba(239,68,68,.07)}
.verdict-icon{font-size:3.8rem;display:block;margin-bottom:.6rem}
.verdict-label{font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;letter-spacing:-.5px;margin-bottom:.25rem}
.c-auth{color:#10b981}.c-sus{color:#f59e0b}.c-mis{color:#ef4444}
.verdict-sub{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#3a5168;font-weight:600}
.pbar-wrap{margin:1.1rem auto 0;max-width:400px}
.pbar-row{display:flex;justify-content:space-between;font-size:.77rem;color:#3a5168;margin-bottom:.4rem}
.pbar-row span:last-child{color:#c8d8e8;font-weight:600}
.pbar-track{background:#0f1e33;border-radius:100px;height:9px;overflow:hidden}
.pbar-fill{height:100%;border-radius:100px}
.tiles{display:grid;gap:.65rem;margin-bottom:1.1rem}
.tiles-4{grid-template-columns:repeat(4,1fr)}.tiles-3{grid-template-columns:repeat(3,1fr)}
.tile{background:#080c15;border:1px solid #0f1e33;border-radius:14px;padding:.9rem .7rem;text-align:center}
.tile-val{font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#38bdf8;line-height:1;margin-bottom:.3rem}
.tile-lbl{font-size:.68rem;text-transform:uppercase;letter-spacing:.07em;color:#2a3f55;font-weight:600}
.sh{font-family:'Syne',sans-serif;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#38bdf8;margin-bottom:.9rem;display:flex;align-items:center;gap:.45rem}
.ev{background:#080c15;border-left:3px solid #1a2e45;border-radius:0 12px 12px 0;padding:.85rem 1.05rem;margin-bottom:.55rem}
.ev.fake{border-left-color:#ef4444}.ev.real{border-left-color:#10b981}.ev.wiki{border-left-color:#38bdf8}.ev.ddg{border-left-color:#fb923c}
.badge{font-size:.67rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:.13rem .5rem;border-radius:6px;display:inline-block;margin-right:.35rem}
.b-ds{background:rgba(99,102,241,.14);color:#818cf8}.b-wiki{background:rgba(56,189,248,.14);color:#38bdf8}.b-ddg{background:rgba(251,146,60,.14);color:#fb923c}.b-fake{background:rgba(239,68,68,.13);color:#f87171}.b-real{background:rgba(16,185,129,.13);color:#34d399}
.fpill{display:inline-block;background:rgba(239,68,68,.09);border:1px solid rgba(239,68,68,.18);border-radius:100px;padding:.18rem .6rem;font-size:.73rem;color:#f87171;margin:.13rem;font-weight:500}
.formula{background:rgba(14,165,233,.04);border:1px solid rgba(14,165,233,.1);border-radius:12px;padding:.95rem 1.25rem;font-family:'Courier New',monospace;font-size:.82rem;color:#7a9ab5;line-height:2;margin-bottom:.9rem}
.formula strong{color:#38bdf8}
.mmatch{background:rgba(245,158,11,.05);border:1px solid rgba(245,158,11,.2);border-radius:14px;padding:.85rem 1.15rem;margin-bottom:1rem}
.empty{text-align:center;padding:5rem 2rem;border:1px dashed #0f1e33;border-radius:18px}
.empty-icon{font-size:2.8rem;margin-bottom:.8rem}
.empty-title{font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;color:#1a2e45;margin-bottom:.4rem}
.empty-sub{font-size:.85rem;color:#0f1e33}
.step{display:flex;align-items:flex-start;gap:.85rem;padding:.55rem 0;border-bottom:1px solid #0f1e33}
.step:last-child{border-bottom:none}
.step-n{width:24px;height:24px;background:rgba(14,165,233,.09);border:1px solid rgba(14,165,233,.18);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:800;color:#38bdf8;flex-shrink:0;margin-top:2px}
.step-t{font-size:.83rem;color:#3a5168;line-height:1.5}
.step-t strong{color:#7a8fa6}
h1,h2,h3,h4,h5,h6{color:#c8d8e8!important}
p,li,label{color:#7a8fa6!important}
.stTextArea textarea,.stTextInput input{background:#080c15!important;border:1px solid #0f1e33!important;border-radius:12px!important;color:#c8d8e8!important}
.stTextArea textarea:focus,.stTextInput input:focus{border-color:#38bdf8!important;box-shadow:0 0 0 2px rgba(14,165,233,.12)!important}
.stButton>button{background:linear-gradient(135deg,#0284c7,#0369a1)!important;color:#fff!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:none!important;border-radius:12px!important;padding:.65rem 1.5rem!important;box-shadow:0 4px 20px rgba(2,132,199,.28)!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(2,132,199,.42)!important}
div[data-testid="stFileUploader"]{background:#080c15!important;border:2px dashed #112240!important;border-radius:14px!important}
div[data-testid="stFileUploader"]:hover{border-color:#38bdf8!important}
.stTabs [data-baseweb="tab-list"]{background:#080c15;border-radius:12px;border:1px solid #0f1e33;gap:2px;padding:3px}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#2a3f55!important;border-radius:9px!important;font-weight:600!important;font-size:.83rem!important}
.stTabs [aria-selected="true"]{background:#0a1e35!important;color:#38bdf8!important}
.stProgress>div>div{background:linear-gradient(90deg,#0284c7,#38bdf8)!important}
.stInfo,.stSuccess,.stWarning,.stError{border-radius:12px!important}
div[data-testid="stToggle"] label span{color:#7a8fa6!important}
</style>
""", unsafe_allow_html=True)

# ── CNN ─────────────────────────────────────────────────────────────
class _CNN(nn.Module):
    def __init__(self):
        super().__init__()
        def blk(i,o): return nn.Sequential(nn.Conv2d(i,o,3,padding=1,bias=False),nn.BatchNorm2d(o),nn.ReLU(True),nn.MaxPool2d(2))
        self.features=nn.Sequential(blk(3,32),blk(32,64),blk(64,128),blk(128,256))
        self.classifier=nn.Sequential(nn.Dropout(.5),nn.Linear(256*16*16,512),nn.ReLU(True),nn.Dropout(.3),nn.Linear(512,128),nn.ReLU(True),nn.Linear(128,1),nn.Sigmoid())
    def forward(self,x): return self.classifier(self.features(x).view(x.size(0),-1))

class Detector:
    _MEAN=[0.485,0.456,0.406];_STD=[0.229,0.224,0.225]
    def __init__(self,path="model.pth"):
        self.device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.demo=True
        self.tf=transforms.Compose([transforms.Resize((256,256)),transforms.ToTensor(),transforms.Normalize(self._MEAN,self._STD)])
        self.model=_CNN().to(self.device)
        if os.path.exists(path):
            try: self.model.load_state_dict(torch.load(path,map_location=self.device)); self.model.eval(); self.demo=False
            except Exception as e: print(f"[WARN] {e}")
    def predict(self,img:Image.Image)->Dict:
        img=img.convert("RGB")
        if not self.demo:
            t=self.tf(img).unsqueeze(0).to(self.device)
            with torch.no_grad(): raw=self.model(t).item()
            pred="Fake" if raw>.5 else "Real"; conf=raw*100 if pred=="Fake" else (1-raw)*100
            return {"prediction":pred,"confidence":round(conf,2),"raw_score":round(raw,4),"mode":"model"}
        arr=np.asarray(img,dtype=np.float32); h,w=arr.shape[:2]; score=0.0
        if w<200 or h<200: score+=.10
        if arr.ndim==3:
            std=arr.std(axis=(0,1)).mean()
            if std<12: score+=.15
            if std>90: score+=.08
            ch=arr.mean(axis=(0,1))
            if ch.max()-ch.min()>80: score+=.10
        rng=np.random.default_rng(int(arr.sum())%(2**32))
        score=float(np.clip(score+rng.uniform(0,.18),0,1))
        pred="Fake" if score>.5 else "Real"; conf=score*100 if pred=="Fake" else (1-score)*100
        return {"prediction":pred,"confidence":round(conf,2),"raw_score":round(score,4),"mode":"demo"}
    def caption_flags(self,caption:str)->Dict:
        flags=[];score=0.0;cap=caption.lower()
        sens=["shocking","unbelievable","miracle","impossible","alien","ghost","conspiracy","cover-up","secret","revealed","proof","confirmed","breakthrough","exposed","they don't want","doctors hate","you won't believe"]
        hits=[w for w in sens if w in cap]
        if hits: score+=min(len(hits)*.08,.4); flags.append(f"Sensational: {', '.join(hits[:3])}")
        for pat,lbl in [(r"\d+\s*%\s*(increase|decrease|reduction|improvement)","Statistical shock"),(r"cure[sd]?\s+\w+","Unverified cure"),(r"prove[sd]?\s+\w+","Definitive proof"),(r"100\s*%\s*(safe|effective|guaranteed)","Absolute guarantee")]:
            if re.search(pat,cap): score+=.12; flags.append(lbl)
        if len(caption)>250: score+=.08; flags.append("Very long caption")
        elif len(caption)<8: score+=.05; flags.append("Very short caption")
        score=float(np.clip(score,0,1))
        return {"consistency_score":round((1-score)*100,2),"inconsistency_score":round(score*100,2),"is_consistent":score<.3,"flags":flags}

# ── RAG ─────────────────────────────────────────────────────────────
_DEMO=[("BREAKING: Miracle cure for cancer that doctors don't want you to know","fake"),("Scientists confirm climate change caused by human activity","real"),("SHOCKING: Government conspiracy revealed","fake"),("Study shows exercise reduces heart disease risk by 30%","real"),("UNBELIEVABLE: Alien spacecraft found, government covering up","fake"),("Researchers develop vaccine with 95% efficacy in trials","real"),("FAKE NEWS: Media lying about election results","fake"),("Economists predict steady growth in tech sector","real"),("MIRACLE: Trick reverses aging overnight, doctors hate it","fake"),("Space agency launches satellite to study climate change","real")]

class RAG:
    EMBED="all-MiniLM-L6-v2"
    def __init__(self,csv="fake_news_dataset.csv"):
        if os.path.exists(csv):
            try:
                df=pd.read_csv(csv)
                for c in ["text","content","article","body","title"]:
                    if c in df.columns: df=df.rename(columns={c:"text"}); break
                if "text" not in df.columns: df["text"]=df.iloc[:,0].astype(str)
                df["text"]=df["text"].fillna("").astype(str); self.df=df
            except Exception: self.df=pd.DataFrame(_DEMO,columns=["text","label"])
        else: self.df=pd.DataFrame(_DEMO,columns=["text","label"])
        self._emb=None;self._idx=None;self._tfidf=None;self._tmat=None
        texts=self.df["text"].tolist()
        if _FAISS_OK:
            try:
                self._emb=SentenceTransformer(self.EMBED)
                vecs=self._emb.encode(texts,show_progress_bar=False,batch_size=64).astype("float32")
                faiss.normalize_L2(vecs); idx=faiss.IndexFlatIP(vecs.shape[1]); idx.add(vecs); self._idx=idx
            except Exception: pass
        if self._idx is None:
            self._tfidf=TfidfVectorizer(max_features=5000,ngram_range=(1,2),stop_words="english")
            self._tmat=self._tfidf.fit_transform(texts)
    def search(self,q:str,k=5)->List[Dict]:
        if self._idx and self._emb:
            qv=self._emb.encode([q],show_progress_bar=False).astype("float32"); faiss.normalize_L2(qv)
            sims,idxs=self._idx.search(qv,k)
            return [{"text":self.df.iloc[i]["text"],"label":self.df.iloc[i].get("label","?"),"similarity":round(float(s),4),"source":"Dataset"} for s,i in zip(sims[0],idxs[0]) if i>=0 and s>.1]
        qv=self._tfidf.transform([q]); sims=sk_cos(qv,self._tmat).flatten(); idxs=sims.argsort()[-k:][::-1]
        return [{"text":self.df.iloc[i]["text"],"label":self.df.iloc[i].get("label","?"),"similarity":round(float(sims[i]),4),"source":"Dataset"} for i in idxs if sims[i]>.05]
    def wikipedia(self,q:str,n=3)->List[Dict]:
        try:
            r=requests.get("https://en.wikipedia.org/w/api.php",params={"action":"query","list":"search","srsearch":q,"format":"json","srlimit":n,"srprop":"snippet"},timeout=7,headers={"User-Agent":"FutureTrust/1.0"})
            out=[]
            for h in r.json().get("query",{}).get("search",[]):
                title=h.get("title",""); snip=re.sub(r"<[^>]+>","",h.get("snippet",""))
                try:
                    r2=requests.get("https://en.wikipedia.org/w/api.php",params={"action":"query","prop":"extracts","pageids":h.get("pageid",0),"format":"json","exintro":True,"explaintext":True},timeout=6,headers={"User-Agent":"FutureTrust/1.0"})
                    extract=next(iter(r2.json().get("query",{}).get("pages",{}).values()),{}).get("extract","")
                except Exception: extract=""
                text=(extract[:500]+"…") if len(extract)>500 else (extract or snip)
                out.append({"title":title,"text":text,"url":f"https://en.wikipedia.org/wiki/{title.replace(' ','_')}","similarity":.75,"source":"Wikipedia","label":""})
            return out
        except Exception: return []
    def patterns(self,q:str)->Dict:
        cats={"sensational":["shocking","unbelievable","miracle","impossible","mind-blowing"],"conspiracy":["conspiracy","cover-up","government hiding","they don't want","suppressed"],"absolute_claims":["proof","confirmed","guaranteed","always","never","100%"],"emotional":["doctors hate","you won't believe","share before deleted","mainstream media lying"],"pseudoscience":["miracle cure","big pharma","detox","frequency healing","quantum healing"]}
        q_low=q.lower(); matches={}; total=0
        for cat,kws in cats.items():
            found=[k for k in kws if k in q_low]; matches[cat]={"matches":found,"count":len(found),"severity":round(len(found)*.2,2)}; total+=len(found)
        risk=min(total*.12,1.0); level="Low" if risk<.3 else ("Medium" if risk<.6 else "High")
        return {"pattern_matches":matches,"total_matches":total,"risk_score":round(risk,3),"risk_level":level}
    def retrieve(self,q:str,use_ds=True,use_web=True)->Dict:
        all_res=[]
        if use_ds: all_res.extend(self.search(q))
        if use_web: all_res.extend(self.wikipedia(q))
        seen=set(); unique=[]
        for r in all_res:
            k=r["text"][:80]
            if k not in seen: seen.add(k); unique.append(r)
        unique.sort(key=lambda x:x["similarity"],reverse=True); top=unique[:6]
        lines=["=== RETRIEVED EVIDENCE ===\n"]
        for i,r in enumerate(top,1):
            lines.append(f"[Source {i}] ({r['source']})")
            if r.get("title"): lines.append(f"  Title: {r['title']}")
            lines.append(f"  Text: {r['text'][:350]}")
            if r.get("url"): lines.append(f"  URL: {r['url']}")
            lines.append(f"  Relevance: {r['similarity']:.2f}")
            if r.get("label") and r["label"] not in ("?","unknown",""): lines.append(f"  Label: {r['label'].upper()}")
            lines.append("")
        return {"context":"\n".join(lines),"sources":top,"query":q}

# ── LLM ─────────────────────────────────────────────────────────────
_MODELS_TRY=["gemini-2.0-flash","gemini-1.5-flash","gemini-1.5-pro","gemini-pro"]

class LLM:
    def __init__(self):
        key=os.getenv("GEMINI_API_KEY","")
        if not key: raise ValueError("GEMINI_API_KEY not set in .env")
        if not _GENAI_OK: raise ImportError("google-genai not installed")
        self.client=genai.Client(api_key=key); self.model=self._pick()
    def _pick(self):
        for m in _MODELS_TRY:
            try: self.client.models.generate_content(model=m,contents="ping"); return m
            except Exception: continue
        return "gemini-2.0-flash"
    def _call(self,p:str)->str:
        try: return self.client.models.generate_content(model=self.model,contents=p).text.strip()
        except Exception as e: return f"[Gemini error: {e}]"
    def fact_check(self,claim:str,ctx:str)->Dict:
        raw=self._call(f'You are a fact-checker. Analyze:\nCLAIM: "{claim}"\nEVIDENCE:\n{ctx}\n\nReturn ONLY JSON (no markdown):\n{{"is_false":<bool>,"falsehood_score":<0.0-1.0>,"reasoning":"<1 sentence>"}}')
        try:
            text=re.sub(r'```json|```','',raw,flags=re.IGNORECASE).strip(); d=json.loads(text)
            return {"is_false":bool(d.get("is_false",False)),"falsehood_score":float(d.get("falsehood_score",0)),"reasoning":str(d.get("reasoning","Checked."))}
        except Exception: return {"is_false":False,"falsehood_score":0.0,"reasoning":"Parse error."}
    def mismatch(self,pred:str,caption:str)->Dict:
        analysis=self._call(f"Image classified as: {pred}\nCaption: \"{caption}\"\n\nIn 3-4 sentences: does the caption match a {pred.lower()} image? Any unverifiable claims? Rate mismatch risk: Low/Medium/High.")
        al=analysis.lower(); risk="High" if ("high" in al and "not high" not in al) else ("Low" if ("low" in al and "not low" not in al) else "Medium")
        return {"analysis":analysis,"risk_level":risk,"mismatch_detected":risk=="High"}
    def explain(self,img_res,cap_res,rag_res,pat_res,scores,caption,is_text=False)->str:
        flags="; ".join(cap_res.get("flags",[])) or "None"
        if is_text:
            return self._call(f'You are an expert AI fact-checker.\nCLAIM: "{caption}"\nEVIDENCE:\n{rag_res.get("context","None")}\nRED FLAGS: {flags}\n\nSTRICT: Do NOT assume true. Check misleading framing, pseudoscience, conspiracy.\n\nOUTPUT:\nStatus: [Authentic / Suspicious / Likely Misleading]\nConfidence: [0-100%]\nReasoning:\n* Bullets (specific, cite evidence)\nTone: Professional, Direct.')
        return self._call(f'You are an expert AI fact-checker.\nIMAGE: {img_res.get("prediction","?")} ({img_res.get("confidence",0):.1f}% confidence)\nCAPTION: "{caption}"\nEVIDENCE:\n{rag_res.get("context","None")}\nRED FLAGS: {flags}\n\nRULES:\n1. Even REAL image can be MISLEADING.\n2. ANY inconsistency → "Likely Misleading".\n3. Fake image → "Fake". Real+mismatch → "Likely Misleading". Suspicious → "Suspicious". All clean → "Authentic".\n\nOUTPUT:\nStatus: [Authentic / Suspicious / Likely Misleading / Fake]\nConfidence: [0-100%]\nReasoning:\n* Bullets (specific, cite evidence)\nTone: Professional, Direct.')
    def ev_summary(self,sources)->str:
        if not sources: return "No relevant evidence retrieved."
        snip=json.dumps([{"src":s["source"],"text":s["text"][:180],"label":s.get("label","")} for s in sources[:5]],indent=2)
        return self._call(f"Summarise in 3 sentences. Corroborated or contradicted?\nSOURCES:\n{snip}")

# ── SCORING ──────────────────────────────────────────────────────────
def score_full(ir,cr,pr,iw=.5,cw=.3,ew=.2)->Dict:
    raw=ir.get("raw_score",.5); pred=ir.get("prediction","Real")
    ic=float(raw) if pred=="Fake" else 1-float(raw); cc=float(cr.get("inconsistency_score",0))/100; ec=float(pr.get("risk_score",0))
    total=iw*ic+cw*cc+ew*ec; label,risk=("Authentic","Low") if total<.30 else (("Suspicious","Medium") if total<.55 else ("Likely Misleading","High"))
    return {"final_score":round(total,4),"ic":round(ic,4),"cc":round(cc,4),"ec":round(ec,4),"final_label":label,"risk_level":risk,"confidence_pct":round((1-total)*100,1)}
def score_text(cr,pr,cw=.5,ew=.5)->Dict:
    cc=float(cr.get("inconsistency_score",0))/100; ec=float(pr.get("risk_score",0)); total=cw*cc+ew*ec
    label,risk=("Authentic","Low") if total<.30 else (("Suspicious","Medium") if total<.55 else ("Likely Misleading","High"))
    return {"final_score":round(total,4),"ic":0.0,"cc":round(cc,4),"ec":round(ec,4),"final_label":label,"risk_level":risk,"confidence_pct":round((1-total)*100,1),"text_only":True}

# ── LOAD ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️ Loading AI models…")
def load_all():
    return Detector(), RAG(), LLM()

def _init():
    for k,v in {"done":False,"res":None}.items():
        if k not in st.session_state: st.session_state[k]=v
_init()
_ok,_err=True,""
try: detector,rag_sys,llm_client=load_all()
except Exception as e: _ok=False;_err=str(e)

# ── PIPELINE ──────────────────────────────────────────────────────────
def run(image,caption,use_ds,use_web,iw,cw,ew):
    prog=st.progress(0);ph=st.empty()
    def step(n,msg):
        prog.progress(n,text=msg)
        ph.markdown(f"<div style='font-size:.78rem;color:#38bdf8;font-weight:600;padding:.35rem .85rem;background:rgba(14,165,233,.06);border:1px solid rgba(14,165,233,.13);border-radius:8px;display:inline-block;margin:.35rem 0;'>{msg}</div>",unsafe_allow_html=True)
    try:
        text_only=image is None
        ir={"raw_score":0.0,"prediction":"Real","confidence":100.0,"mode":"none"}
        if not text_only: step(10,"🖼️ Analysing image…"); ir=detector.predict(image)
        step(22,"📝 Scanning caption…"); cr=detector.caption_flags(caption)
        mr=None
        if not text_only: step(34,"🔗 Checking mismatch…"); mr=llm_client.mismatch(ir["prediction"],caption)
        if mr and mr["mismatch_detected"]: cr["inconsistency_score"]=min(cr.get("inconsistency_score",0)+40,100)
        step(45,"🔎 Detecting patterns…"); pr=rag_sys.patterns(caption)
        step(58,"📚 Retrieving evidence…"); rr=rag_sys.retrieve(caption,use_ds,use_web)
        step(70,"🧠 Fact-checking…"); truth=llm_client.fact_check(caption,rr["context"])
        ts=truth.get("falsehood_score",0); combined=max(pr.get("risk_score",0),ts); pr["risk_score"]=combined
        if truth.get("is_false") or ts>=.3:
            pr.setdefault("pattern_matches",{})
            if combined>=.6: pr["risk_level"]="High"; cr["inconsistency_score"]=max(cr.get("inconsistency_score",0),80); cr.setdefault("flags",[]); cr["flags"].append("Fact-checked false") if "Fact-checked false" not in cr["flags"] else None
            elif combined>=.3: pr["risk_level"]="Medium"
            pr["pattern_matches"]["factual_error"]={"matches":[truth.get("reasoning","Error")],"count":1,"severity":ts}
        step(80,"⚖️ Scoring…")
        sc=score_text(cr,pr,cw/(cw+ew+1e-9),ew/(cw+ew+1e-9)) if text_only else score_full(ir,cr,pr,iw,cw,ew)
        step(90,"🤖 Generating explanation…"); expl=llm_client.explain(ir,cr,rr,pr,sc,caption,text_only)
        if expl.startswith("[Gemini error:"): raise RuntimeError(expl)
        step(97,"📋 Summarising evidence…"); ev_sum=llm_client.ev_summary(rr["sources"])
        prog.progress(100,text="✅ Done!"); ph.empty()
        st.session_state.res={"sc":sc,"ir":ir,"mr":mr,"cr":cr,"pr":pr,"rr":rr,"expl":expl,"ev_sum":ev_sum,"caption":caption,"text_only":text_only}
        st.session_state.done=True; st.rerun()
    except Exception:
        prog.empty();ph.empty();st.error(f"❌ Failed:\n```\n{traceback.format_exc()}\n```");st.session_state.done=False

# ── DISPLAY ───────────────────────────────────────────────────────────
def show(res):
    sc=res["sc"];ir=res.get("ir");mr=res.get("mr");cr=res["cr"];pr=res["pr"];rr=res["rr"];is_text=res.get("text_only",False)
    label=sc["final_label"];risk=sc["risk_level"]
    vcss={"Authentic":"v-authentic","Suspicious":"v-suspicious","Likely Misleading":"v-misleading"}.get(label,"v-suspicious")
    lcss={"Authentic":"c-auth","Suspicious":"c-sus","Likely Misleading":"c-mis"}.get(label,"c-sus")
    icon={"Authentic":"✅","Suspicious":"⚠️","Likely Misleading":"🚨"}.get(label,"❓")
    bar={"Authentic":"#10b981","Suspicious":"#f59e0b","Likely Misleading":"#ef4444"}.get(label,"#f59e0b")
    if mr and mr.get("mismatch_detected"):
        st.markdown(f'<div class="mmatch"><div style="font-size:.8rem;font-weight:700;color:#f59e0b;margin-bottom:.3rem;">⚠️ Image–Caption Mismatch</div><div style="font-size:.81rem;color:#7a8fa6;">{mr["analysis"]}</div></div>',unsafe_allow_html=True)
    auth=round((1-sc["final_score"])*100,1)
    st.markdown(f'<div class="verdict {vcss}"><span class="verdict-icon">{icon}</span><div class="verdict-label {lcss}">{label.upper()}</div><div class="verdict-sub">Risk · {risk}</div><div class="pbar-wrap"><div class="pbar-row"><span>{"Authenticity" if not is_text else "Credibility"}</span><span>{auth}%</span></div><div class="pbar-track"><div class="pbar-fill" style="width:{auth}%;background:{bar};"></div></div></div></div>',unsafe_allow_html=True)
    tiles=[(ir.get("prediction","?") if ir else "N/A","🖼️ Image"),(f'{ir.get("confidence",0):.0f}%' if ir else "N/A","🎯 Confidence"),(f'{cr["consistency_score"]:.0f}%',"📝 Consistency"),(pr["risk_level"],"⚠️ Pattern")] if not is_text else [("N/A","🖼️ Image"),(f'{cr["consistency_score"]:.0f}%',"📝 Consistency"),(pr["risk_level"],"⚠️ Pattern")]
    tc="tiles-3" if is_text else "tiles-4"
    tiles_html="".join(f'<div class="tile"><div class="tile-val">{v}</div><div class="tile-lbl">{l}</div></div>' for v,l in tiles)
    st.markdown(f'<div class="tiles {tc}">{tiles_html}</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["🤖 AI Explanation","📚 Evidence","📊 Signals"])
    with t1:
        st.markdown("<div class='sh'>🧠 Gemini Analysis</div>",unsafe_allow_html=True)
        st.markdown("\n".join(f"**{ln.strip()}**" if ln.strip().startswith("Status:") else ln for ln in res["expl"].split("\n")))
    with t2:
        st.markdown("<div class='sh'>📋 Summary</div>",unsafe_allow_html=True)
        st.markdown(f'<div class="card card-tight"><p style="color:#7a8fa6;margin:0;font-size:.86rem;">{res["ev_sum"]}</p></div>',unsafe_allow_html=True)
        sources=rr.get("sources",[])
        if sources:
            st.markdown("<div class='sh' style='margin-top:.9rem;'>🗄️ Sources</div>",unsafe_allow_html=True)
            for s in sources:
                src=s.get("source","?");lbl=s.get("label","");title=s.get("title","");text=s.get("text","")[:300];url=s.get("url","");sim=s.get("similarity",0)
                ev_cls="wiki" if src=="Wikipedia" else ("ddg" if src=="DuckDuckGo" else ("fake" if lbl=="fake" else ("real" if lbl=="real" else "")))
                b_cls="b-wiki" if src=="Wikipedia" else ("b-ddg" if src=="DuckDuckGo" else "b-ds")
                bh=f'<span class="badge {b_cls}">{src}</span>'+(f'<span class="badge b-{lbl}">{lbl.upper()}</span>' if lbl else "")
                uh=f'<div style="margin-top:.45rem;"><a href="{url}" target="_blank" style="color:#38bdf8;font-size:.73rem;">🔗 {url[:65]}</a></div>' if url else ""
                th2=f'<div style="font-weight:600;color:#c8d8e8;font-size:.83rem;margin:.25rem 0;">{title}</div>' if title else ""
                st.markdown(f'<div class="ev {ev_cls}"><div style="display:flex;justify-content:space-between;align-items:center;"><div>{bh}</div><span style="font-size:.7rem;color:#1a2e45;">sim {sim:.2f}</span></div>{th2}<div style="color:#3a5168;font-size:.8rem;line-height:1.55;">{text}</div>{uh}</div>',unsafe_allow_html=True)
        else: st.info("No sources retrieved.")
    with t3:
        st.markdown("<div class='sh'>⚖️ Formula</div>",unsafe_allow_html=True)
        cc=sc["cc"];ec=sc["ec"];fs=sc["final_score"]
        if is_text: fh=f"final_score = 0.50 × {cc:.4f} (context)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.50 × {ec:.4f} (patterns)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <strong>{fs:.4f}</strong> → {label}"
        else: ic=sc["ic"]; fh=f"final_score = 0.50 × {ic:.4f} (image)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.30 × {cc:.4f} (context)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ 0.20 × {ec:.4f} (patterns)<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <strong>{fs:.4f}</strong> → {label}"
        st.markdown(f'<div class="formula">{fh}</div>',unsafe_allow_html=True)
        if not is_text and ir:
            c1,c2,c3=st.columns(3); c1.metric("Image",ir.get("prediction","?")); c2.metric("Confidence",f'{ir.get("confidence",0):.1f}%'); c3.metric("Mode",ir.get("mode","—").title())
        st.markdown("<div class='sh' style='margin-top:.9rem;'>🚩 Red Flags</div>",unsafe_allow_html=True)
        flags=cr.get("flags",[])
        if flags: st.markdown(" ".join(f'<span class="fpill">⚑ {f}</span>' for f in flags),unsafe_allow_html=True)
        else: st.success("✅ No red flags.")
        st.markdown("<div class='sh' style='margin-top:.9rem;'>🔎 Patterns</div>",unsafe_allow_html=True)
        pm=pr.get("pattern_matches",{});found=False
        for cat,info in pm.items():
            if info.get("matches"):
                found=True; pills=" ".join(f'<span class="fpill">{m}</span>' for m in info["matches"])
                st.markdown(f'<div style="margin-bottom:.5rem;"><span style="font-size:.75rem;font-weight:700;color:#7a8fa6;text-transform:uppercase;">{cat.replace("_"," ").title()}</span><br>{pills}</div>',unsafe_allow_html=True)
        if not found: st.success("✅ No suspicious patterns.")

# ── SIDEBAR ───────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div style="text-align:center;padding:1.1rem 0 1rem;border-bottom:1px solid #0f1e33;margin-bottom:1.1rem;"><div style="font-size:1.8rem;">🛡️</div><div style="font-family:\'Syne\',sans-serif;font-size:.88rem;font-weight:700;color:#c8d8e8;">FutureTrust</div><div style="font-size:.68rem;color:#1a2e45;margin-top:.2rem;">Misinformation Detector · 2025</div></div>',unsafe_allow_html=True)
        st.markdown("#### ⚙️ Data Sources")
        use_ds=st.toggle("📂 Local Dataset",value=True); use_web=st.toggle("🌐 Wikipedia",value=True)
        st.markdown("#### ⚖️ Score Weights")
        iw=st.slider("🖼️ Image",0.1,0.8,0.50,0.05); cw=st.slider("📝 Context",0.1,0.6,0.30,0.05); ew=round(max(1.0-iw-cw,0.05),2)
        st.info(f"🗄️ Evidence: **{ew:.2f}** (auto)")
        st.markdown("#### 📊 Status")
        if _ok:
            n=len(rag_sys.df) if hasattr(rag_sys,"df") else 0; idx="FAISS" if (hasattr(rag_sys,"_idx") and rag_sys._idx) else "TF-IDF"
            st.success("✅ All modules loaded")
            st.markdown(f'<div style="font-size:.76rem;color:#1a3a55;line-height:1.9;">🤖 CNN · RAG · Gemini<br>📦 Dataset: {n:,} rows<br>🔬 Index: {idx}</div>',unsafe_allow_html=True)
        else: st.error(f"❌ {_err}")
        st.markdown("---")
        if st.button("🗑️ Reset",use_container_width=True): st.session_state.done=False;st.session_state.res=None;st.rerun()
    return {"use_ds":use_ds,"use_web":use_web,"iw":iw,"cw":cw,"ew":ew}

# ── MAIN ──────────────────────────────────────────────────────────────
def main():
    cfg=sidebar()
    st.markdown('<div class="hero"><div class="hero-badge">🛡️ AI-Powered Fact Verification</div><div class="hero-title">AI Misinformation<br><em>Detection System</em></div><p class="hero-sub">Multi-signal analysis combining computer vision, semantic retrieval, and LLM reasoning to detect fake or misleading content in real time.</p><div class="hero-chips"><span class="chip">🖼️ Image CNN</span><span class="chip">📚 FAISS RAG</span><span class="chip">🤖 Gemini LLM</span><span class="chip">🔎 Pattern Detection</span><span class="chip">🌐 Wikipedia</span></div></div>',unsafe_allow_html=True)
    if not _ok: st.error(f"🚫 {_err}"); return
    left,right=st.columns([1,1.1],gap="large")
    with left:
        st.markdown("<div class='sh'>📤 Input</div>",unsafe_allow_html=True)
        mode=st.radio("Mode",["Image + Caption","Text Only"],horizontal=True,label_visibility="collapsed")
        text_mode=mode=="Text Only"; image=None
        if not text_mode:
            up=st.file_uploader("Upload image",type=["jpg","jpeg","png","webp","gif"])
            if up: image=Image.open(up).convert("RGB"); st.image(image,caption="Uploaded image",use_container_width=True)
        caption=st.text_area("📝 Paste claim / caption",placeholder="Paste a news headline, tweet, or caption to verify…",height=150 if text_mode else 110)
        btn=st.button("🚀 Analyse",type="primary",use_container_width=True,disabled=not _ok)
        if btn:
            st.session_state.done=False
            if text_mode and not (caption or "").strip(): st.warning("⚠️ Enter a claim first.")
            elif not text_mode and image is None: st.warning("⚠️ Upload an image first.")
            else:
                with st.spinner(""): run(image,(caption or "").strip(),cfg["use_ds"],cfg["use_web"],cfg["iw"],cfg["cw"],cfg["ew"])
        if not st.session_state.done:
            st.markdown("<div style='height:.8rem'></div>",unsafe_allow_html=True)
            st.markdown("<div class='sh'>💡 How it works</div>",unsafe_allow_html=True)
            for n,t in [("1","Choose <strong>Image+Caption</strong> or <strong>Text Only</strong>"),("2","Upload image and/or paste the claim"),("3","Click <strong>Analyse</strong>"),("4","Get a multi-signal verdict + evidence trail")]:
                st.markdown(f'<div class="step"><div class="step-n">{n}</div><div class="step-t">{t}</div></div>',unsafe_allow_html=True)
    with right:
        st.markdown("<div class='sh'>📊 Results</div>",unsafe_allow_html=True)
        if st.session_state.done and st.session_state.res: show(st.session_state.res)
        else: st.markdown('<div class="empty"><div class="empty-icon">🎯</div><div class="empty-title">Ready for Analysis</div><div class="empty-sub">Submit a claim or image to get a verdict.</div></div>',unsafe_allow_html=True)

if __name__=="__main__":
    main()
