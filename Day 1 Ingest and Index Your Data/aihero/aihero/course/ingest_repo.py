# ingest_repo.py
import io
import os
import sys
import json
import zipfile
import requests
import frontmatter
from typing import List, Dict

def zip_url(repo_owner: str, repo_name: str, branch: str) -> str:
    # GitHub "codeload" zip endpoint
    return f"https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/{branch}"

def try_download(repo_owner: str, repo_name: str, branches=("main", "master")) -> bytes:
    last_status = None
    for br in branches:
        url = zip_url(repo_owner, repo_name, br)
        resp = requests.get(url, timeout=60)
        last_status = resp.status_code
        if resp.status_code == 200:
            return resp.content
    raise RuntimeError(f"Failed to download zip for {repo_owner}/{repo_name} "
                       f"(tried branches: {branches}, last status: {last_status})")

def read_repo_data(repo_owner: str, repo_name: str, exts=(".md", ".mdx")) -> List[Dict]:
    """
    Download repo zip, parse .md/.mdx with frontmatter, return list of dicts:
    { 'source': 'owner/repo', 'filename': 'path/in/repo.md', 'metadata': {...}, 'content': '...' }
    """
    blob = try_download(repo_owner, repo_name, branches=("main", "master"))
    zf = zipfile.ZipFile(io.BytesIO(blob))
    out: List[Dict] = []

    for info in zf.infolist():
        # Skip directories
        if info.is_dir():
            continue

        filename = info.filename  # includes top-level "<repo>-<branch>/..."
        low = filename.lower()

        if not low.endswith(exts):
            continue

        try:
            with zf.open(info) as f:
                # decode to text; ignore weird encodings safely
                text = f.read().decode("utf-8", errors="ignore")
                post = frontmatter.loads(text)
                data = {
                    "source": f"{repo_owner}/{repo_name}",
                    "filename": "/".join(filename.split("/")[1:]),  # strip top folder
                    "metadata": post.metadata or {},
                    "content": post.content or "",
                }
                out.append(data)
        except Exception as e:
            # Non-fatal: continue processing
            print(f"[WARN] Error processing {filename}: {e}")

    zf.close()
    return out

def save_jsonl(records: List[Dict], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: uv run python ingest_repo.py <repo_owner> <repo_name> [output.jsonl]")
        print("Example: uv run python ingest_repo.py DataTalksClub faq dtc_faq.jsonl")
        sys.exit(1)

    owner = sys.argv[1]
    name = sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else f"{owner}_{name}.jsonl"

    print(f"[INFO] Downloading and parsing {owner}/{name} ...")
    records = read_repo_data(owner, name)
    print(f"[INFO] Parsed {len(records)} docs (.md/.mdx)")

    save_jsonl(records, out_file)
    print(f"[OK] Saved -> {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()
