import io, os, sys, json, re, zipfile, argparse
from typing import List, Dict

import requests

# ---- Safe frontmatter parser (no external deps) ----
_FM_START = re.compile(r"^---\s*$", re.MULTILINE)

def parse_frontmatter_safely(text: str) -> (Dict, str):
    """
    Returns (metadata_dict, content_str).
    If no YAML frontmatter, metadata={}, content=text.
    If YAML block exists but no yaml lib, returns {} and full content after frontmatter.
    """
    if not text.startswith("---"):
        return {}, text

    # Find the first two '---' lines
    matches = list(_FM_START.finditer(text))
    if len(matches) < 2 or matches[0].start() != 0:
        return {}, text

    start = matches[0].end()
    end = matches[1].start()
    raw_yaml = text[start:end].strip()
    body = text[matches[1].end():].lstrip("\n")

    # Try to parse YAML if pyyaml is available; otherwise return empty metadata
    meta = {}
    try:
        import yaml  # optional
        meta = yaml.safe_load(raw_yaml) or {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        # no yaml or bad yaml: keep meta empty, still return body
        meta = {}

    return meta, body

# ---------- Day 1 helpers: download & parse .md/.mdx ----------
def zip_url(owner: str, repo: str, branch: str) -> str:
    return f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"

def try_download(owner: str, repo: str, branches=("main","master")) -> bytes:
    last_status = None
    for br in branches:
        resp = requests.get(zip_url(owner, repo, br), timeout=60)
        last_status = resp.status_code
        if resp.status_code == 200:
            return resp.content
    raise RuntimeError(f"Failed to download {owner}/{repo} (tried {branches}, last={last_status})")

def read_repo_docs(owner: str, repo: str, exts=(".md", ".mdx")) -> List[Dict]:
    blob = try_download(owner, repo, branches=("main","master"))
    zf = zipfile.ZipFile(io.BytesIO(blob))
    out: List[Dict] = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        filename = info.filename
        if not filename.lower().endswith(exts):
            continue
        try:
            with zf.open(info) as f:
                text = f.read().decode("utf-8", errors="ignore")
                metadata, content = parse_frontmatter_safely(text)
                out.append({
                    "source": f"{owner}/{repo}",
                    "filename": "/".join(filename.split("/")[1:]),  # strip top folder
                    "metadata": metadata,
                    "content": content
                })
        except Exception as e:
            print(f"[WARN] {filename}: {e}")
    zf.close()
    return out

# ---------- Chunkers ----------
def sliding_window(text: str, size: int = 2000, overlap: int = 1000):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size>0 and 0<=overlap<size")
    step = size - overlap
    n = len(text)
    i = 0
    idx = 0
    while i < n:
        chunk = text[i:i+size]
        yield {"chunk_index": idx, "start": i, "end": i+len(chunk), "text": chunk}
        idx += 1
        if i + size >= n:
            break
        i += step

_paragraph_splitter = re.compile(r"\n\s*\n", re.MULTILINE)
def split_paragraphs(text: str):
    return [p.strip() for p in _paragraph_splitter.split(text.strip()) if p.strip()]

def split_markdown_by_level(text: str, level: int = 2):
    header_pattern = r'^(#{' + str(level) + r'}\s+.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)
    parts = pattern.split(text)
    if len(parts) <= 1:
        return [text.strip()] if text.strip() else []
    sections = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        after = parts[i+1].strip() if (i+1) < len(parts) else ""
        block = f"{header}\n\n{after}".strip()
        if block:
            sections.append(block)
    return sections

# ---------- Output ----------
def write_jsonl(records: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="evidentlyai")
    ap.add_argument("--repo", default="docs")
    ap.add_argument("--size", type=int, default=2000)
    ap.add_argument("--overlap", type=int, default=1000)
    ap.add_argument("--section_level", type=int, default=2)
    args = ap.parse_args()

    print(f"[INFO] Downloading {args.owner}/{args.repo} ...")
    docs = read_repo_docs(args.owner, args.repo)
    docs = [d for d in docs if (d.get("content") or "").strip()]
    print(f"[INFO] Parsed {len(docs)} docs with content")

    sliding_out = []
    for d in docs:
        for c in sliding_window(d["content"], size=args.size, overlap=args.overlap):
            sliding_out.append({
                "split_type": "sliding",
                "source": d["source"],
                "filename": d["filename"],
                "metadata": d["metadata"],
                "start": c["start"],
                "end": c["end"],
                "text": c["text"]
            })
    write_jsonl(sliding_out, "evidently_sliding.jsonl")
    print(f"[OK] sliding -> evidently_sliding.jsonl  (chunks: {len(sliding_out)})")

    para_out = []
    for d in docs:
        paras = split_paragraphs(d["content"])
        for i, p in enumerate(paras):
            para_out.append({
                "split_type": "paragraph",
                "source": d["source"],
                "filename": d["filename"],
                "metadata": d["metadata"],
                "paragraph_index": i,
                "text": p
            })
    write_jsonl(para_out, "evidently_paragraph.jsonl")
    print(f"[OK] paragraph -> evidently_paragraph.jsonl (chunks: {len(para_out)})")

    sect_out = []
    for d in docs:
        secs = split_markdown_by_level(d["content"], level=args.section_level)
        for i, s in enumerate(secs):
            sect_out.append({
                "split_type": "section",
                "source": d["source"],
                "filename": d["filename"],
                "metadata": d["metadata"],
                "section_index": i,
                "text": s
            })
    write_jsonl(sect_out, "evidently_section.jsonl")
    print(f"[OK] section -> evidently_section.jsonl (chunks: {len(sect_out)})")

    print("\n[SUMMARY]")
    print(f"  Sliding chunks : {len(sliding_out)}  (size={args.size}, overlap={args.overlap})")
    print(f"  Paragraph chunks: {len(para_out)}")
    print(f"  Section chunks  : {len(sect_out)}  (level={args.section_level})")

if __name__ == "__main__":
    main()
