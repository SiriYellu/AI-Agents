<img width="2047" height="829" alt="Screenshot 2025-09-25 213608" src="https://github.com/user-attachments/assets/867398fc-848f-4d0c-aacb-d7f130602019" />

# Day 1 – Ingest and Index Your Data

📚 **Learning Log – Day 1 of AI Agents Crash Course**

Today I learned how to **ingest data from GitHub repositories** and prepare it for use in an AI system.  
This step is like “collecting the ingredients” before we can build the actual agent.

---

## What I Learned
- How to **download GitHub repos** directly as zip archives using `requests`.
- How to **parse Markdown files** (`.md`, `.mdx`) and extract:
  - Metadata (frontmatter in YAML format)
  - Main document content
- How to store parsed documents into a structured format (`.jsonl`) for later indexing.
- Why **frontmatter** is useful: it provides structured info like title, tags, and difficulty.

---

## Methods Implemented
1. **Download Repos as Zip**
   - Used `requests` + `zipfile` + `io.BytesIO`.
   - No need to save the archive to disk.

2. **Parse Markdown with Frontmatter**
   - Extracted metadata (`title`, `tags`, etc.).
   - Extracted clean content for each file.

3. **Reusable Function**
   - Wrote `read_repo_data(owner, repo)` to process any repo.
   - Output is a list of dictionaries with filename, metadata, and content.

---

## Outputs
Tested with:
- [DataTalksClub/faq](https://github.com/DataTalksClub/faq) ✅ small FAQ-style docs
- [evidentlyai/docs](https://github.com/evidentlyai/docs) ✅ large technical docs

Created JSONL outputs such as:
dtc_faq.jsonl
evidently_docs.jsonl
---

## Key Insight
✨ Even before building an AI agent, **clean and structured data ingestion is critical**.  
If your data isn’t organized, no search or AI system will work well.

---

## Next Step
Tomorrow → **Chunking large documents** into smaller, context-friendly pieces for search and LLMs. 🚀
