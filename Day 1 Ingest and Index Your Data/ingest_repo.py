import io, os, sys, json, zipfile, requests, frontmatter
from typing import List, Dict

def zip_url(owner: str, repo: str, branch: str) -> str:
    return f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"

def try_download(owner: str, repo: str, branches=("main","master")) -> bytes:
    last_status = None
    for br in branches:
        url = zip_url(owner, repo, br)
        resp = requests.get(url, timeout=60)
        last_status = resp.status_code
        if resp.status_code == 200:
            return resp.content
    raise RuntimeError(f"Failed to download {owner}/{repo} (tried {branches}, last status={last_status})")

def read_repo_data(owner: str, repo: str, exts=(".md", ".mdx")) -> List[Dict]:
    blob = try_download(owner, repo, branches=("main","master"))
    zf = zipfile.ZipFile(io.BytesIO(blob))
    out: List[Dict] = []
    for info in zf.infolist():
        if info.is_dir(): continue
        filename = info.filename
        if not filename.lower().endswith(exts): continue
        try:
            with zf.open(info) as f:
                text = f.read().decode("utf-8", errors="ignore")
                post = frontmatter.loads(text)
                out.append({
                    "source": f"{owner}/{repo}",
                    "filename": "/".join(filename.split("/")[1:]),
                    "metadata": post.metadata or {},
                    "content": post.content or ""
                })
        except Exception as e:
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
        sys.exit(1)
    owner, name = sys.argv[1], sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) > 3 else f"{owner}_{name}.jsonl"
    print(f"[INFO] Downloading and parsing {owner}/{name} ...")
    records = read_repo_data(owner, name)
    print(f"[INFO] Parsed {len(records)} docs (.md/.mdx)")
    save_jsonl(records, out_file)
    print(f"[OK] Saved -> {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()
