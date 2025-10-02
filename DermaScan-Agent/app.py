# -----------------------------------------------------------
# DermaScan Repo Assistant — Streamlit UI with Gemini + Fallback + BG + Chat Bubbles
# -----------------------------------------------------------
import os, io, json, zipfile, secrets, re, base64
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Dict, Any, Tuple

import streamlit as st
import requests
from minsearch import Index

# Gemini optional
try:
    import google.generativeai as genai
except Exception:
    genai = None

# ===================== CONFIG =====================
DEFAULT_REPO_OWNER = "SiriYellu"
DEFAULT_REPO_NAME  = "DermaScan_AndroidApp"

TEXT_EXTS  = (".md", ".mdx", ".txt", ".java", ".kt", ".xml", ".py", ".rst")
WINDOW     = 1000
STRIDE     = 500
MODEL_TRY  = [
    "gemini-2.5-flash",
    "gemini-pro-latest",
    "gemini-2.0-flash",
]
# ==================================================

# ----------------- Helpers -----------------
def now_iso() -> str:
    return datetime.now(UTC).isoformat()

def ts_compact() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

def human_file(path: str) -> str:
    return Path(path).name

def badge(text: str) -> str:
    return f"<span class='badge'>{text}</span>"

def sanitize_md(s: str, limit: int = 1200) -> str:
    s = (s or "").strip()
    s = re.sub(r"\n{3,}", "\n\n", s)
    if len(s) > limit:
        s = s[:limit] + "..."
    return s

def get_base64_of_bin_file(bin_file: str) -> str:
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()
# -------------------------------------------

# ----------------- Theming -----------------
st.set_page_config(page_title="DermaScan Agent", page_icon="🩺", layout="wide")

# Background image (base64 so it works from Colab)
bg_path = "DermaScan-Agent/Gemini_Generated_Image_msjjscmsjjscmsjj.png"  # <- your file
bg_css = ""
try:
    bg_base64 = get_base64_of_bin_file(bg_path)
    bg_css = f"""
      .stApp {{
        background: url("data:image/png;base64,{bg_base64}") no-repeat center center fixed;
        background-size: cover;
      }}
    """
except Exception as e:
    # no image is okay – we still render the rest
    pass

st.markdown(
    f"""
    <style>
      {bg_css}
      :root {{
        --accent:#7c83ff; --bg:#0f1117; --panel:#111421; --text:#eaeefb; --muted:#9aa4b2;
      }}
      .main, .stApp {{ color: var(--text); }}

      /* Small pill/badges for sources */
      .badge {{
        display:inline-block; padding:4px 8px; border-radius:8px;
        background:#1b1f2e; border:1px solid #283148; color:#c6d0e4;
        font-size:12px; margin:0 6px 6px 0;
      }}

      /* Chat “bubble” look (semi-transparent black boxes) */
      .bubble {{
        background: rgba(7, 10, 18, 0.66);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        backdrop-filter: saturate(120%) blur(2px);
      }}
      .bubble.question {{
        background: rgba(21, 23, 31, 0.65);
        border: 1px solid rgba(124, 131, 255, 0.18);
      }}
      .bubble.answer {{
        background: rgba(12, 14, 22, 0.72);
        border: 1px solid rgba(72, 81, 130, 0.25);
      }}
      .sources-row {{ margin-top: 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)
# -------------------------------------------

# ---------------- Ingestion ----------------
@st.cache_resource(show_spinner=True)
def ingest_repo(owner: str, name: str, exts: tuple, window: int, stride: int) -> Tuple[Index, List[Dict[str,Any]]]:
    """Download GitHub repo as ZIP, extract text files, chunk, and build lexical index."""
    url = f"https://codeload.github.com/{owner}/{name}/zip/refs/heads/main"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    docs: List[Dict[str,Any]] = []
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for info in zf.infolist():
            fn = info.filename
            if not fn.lower().endswith(exts):
                continue
            try:
                with zf.open(info) as f:
                    raw = f.read().decode("utf-8", errors="ignore")
            except Exception:
                continue
            try:
                _, rel = fn.split("/", maxsplit=1)
            except ValueError:
                rel = fn
            docs.append({"filename": rel, "title": Path(rel).stem, "content": raw})

    chunks = []
    for d in docs:
        text = d["content"] or ""
        n = len(text); i = 0
        if n == 0:
            continue
        while i < n:
            piece = text[i:i+window]
            chunks.append({"content": piece, "filename": d["filename"], "title": d["title"]})
            i += stride
            # tail coverage
            if i >= n and i - stride + window < n:
                tail_start = max(0, n - window)
                tail_piece = text[tail_start:n]
                if not chunks or chunks[-1]["content"] != tail_piece:
                    chunks.append({"content": tail_piece, "filename": d["filename"], "title": d["title"]})
                break

    index = Index(text_fields=["content", "title", "filename"])
    index.fit(chunks)
    return index, chunks
# -------------------------------------------

# --------------- Answering -----------------
def make_context(results: List[Dict[str,Any]], topk: int) -> str:
    parts = []
    for r in results[:topk]:
        fn = r.get("filename","")
        body = sanitize_md(r.get("content",""), limit=2000)
        parts.append(f"[FILE: {fn}]\n{body}")
    return "\n\n---\n\n".join(parts) if parts else "(no results)"

def try_gemini_answer(question: str, context: str) -> tuple[str | None, str | None]:
    if genai is None: return None, None
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key: return None, None
    try:
        genai.configure(api_key=key)
    except Exception:
        return None, None

    system_rules = (
        "Answer ONLY from the provided repo context. "
        "Cite filenames inline. If not found, reply: 'Not found in repo.'"
    )
    prompt = f"{system_rules}\n\n# Context\n{context}\n\n# Q\n{question}"

    last_err = None
    for model_name in MODEL_TRY:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            text = (resp.text or "").strip()
            if text:
                return text, model_name
        except Exception as e:
            last_err = e
    return None, None

def answer_with_repo(q: str, index: Index, topk: int = 5):
    results = index.search(q, num_results=max(1, topk))
    if not results:
        return "Not found in repo.", [], [], "No results"

    context = make_context(results, topk)
    ans, model_used = try_gemini_answer(q, context)
    if ans:
        used_files = [r.get("filename","") for r in results[:topk]]
        return ans, used_files, results, f"Gemini ({model_used})"

    # Fallback to lexical: show the best snippet
    best = results[0]
    snippet = sanitize_md(best.get("content",""), limit=800)
    used_files = [r.get("filename","") for r in results[:topk]]
    return (
        f"From `{best.get('filename','')}`:\n\n{snippet}\n\n*(LLM unavailable — lexical fallback)*",
        used_files, results, "Lexical"
    )
# -------------------------------------------

# ===================== UI =====================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    repo_owner = st.text_input("Repo owner", value=DEFAULT_REPO_OWNER)
    repo_name  = st.text_input("Repo name",  value=DEFAULT_REPO_NAME)
    topk = st.slider("Results to use for context", 3, 10, 6, 1)
    gemini_on = bool(os.environ.get("GEMINI_API_KEY","").strip()) and (genai is not None)
    st.markdown(f"Gemini key detected: **{'Yes' if gemini_on else 'No'}**")

st.title("🩺 DermaScan Repo Assistant")
st.caption("Grounded answers from your repository — datasets, models, deployment, and more.")

with st.spinner("📥 Indexing repo…"):
    index, chunks = ingest_repo(repo_owner, repo_name, TEXT_EXTS, WINDOW, STRIDE)
st.success(f"Indexed {len(chunks)} chunks.")

# Chat history store
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history with bubbles
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        klass = "question" if m["role"] == "user" else "answer"
        st.markdown(f"<div class='bubble {klass}'>{m['content']}</div>", unsafe_allow_html=True)

# Chat input -> ask
q = st.chat_input("Ask about datasets, models, deployment, files, etc.")
if q:
    # USER BUBBLE
    st.session_state.messages.append({"role":"user","content":q})
    with st.chat_message("user"):
        st.markdown(f"<div class='bubble question'>{q}</div>", unsafe_allow_html=True)

    # ASSISTANT BUBBLE
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching repo…"):
            answer, used_files, results, model_used = answer_with_repo(q, index=index, topk=topk)

            # Sources badges
            sources_html = ""
            if used_files:
                badges = " ".join(badge(human_file(f)) for f in used_files if f)
                sources_html = f"<div class='sources-row'><strong>Sources:</strong> {badges}</div>"

            answer_html = f"{answer}{sources_html}"
            st.markdown(f"<div class='bubble answer'>{answer_html}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role":"assistant","content":answer})
