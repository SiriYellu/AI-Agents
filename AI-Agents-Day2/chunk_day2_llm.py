import os, json
from typing import List, Dict
from tqdm.auto import tqdm
from openai import OpenAI
from dotenv import load_dotenv

from chunk_day2 import read_repo_docs  # uses safe parser

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in .env")
client = OpenAI(api_key=api_key)

PROMPT = """
Split the provided document into logical sections that make sense for a Q&A system.
Each section should be self-contained and cover a specific topic or concept.

<DOCUMENT>
{document}
</DOCUMENT>

Use this exact format:

## Section Name

Section content with all relevant details

---

""".strip()

def llm_sections(text: str, model: str = "gpt-4o-mini") -> List[str]:
    prompt = PROMPT.format(document=text)
    resp = client.responses.create(model=model, input=[{"role":"user","content":prompt}])
    out = resp.output_text or ""
    return [p.strip() for p in out.split("---") if p.strip()]

def main():
    docs = read_repo_docs("evidentlyai", "docs")
    docs = [d for d in docs if (d.get("content") or "").strip()]

    results: List[Dict] = []
    for d in tqdm(docs, desc="LLM chunking"):
        sections = llm_sections(d["content"])
        for i, s in enumerate(sections):
            results.append({
                "split_type": "llm",
                "source": d["source"],
                "filename": d["filename"],
                "metadata": d["metadata"],
                "section_index": i,
                "text": s
            })

    with open("evidently_llm.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
