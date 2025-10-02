# AI-Agents
<!-- ====== HERO / LIVE LINK ====== -->

# 🩺 DermaScan Repo Assistant

<p align="center">
  <a href="https://ai-agents-dermascan.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/Live%20App-Open%20in%20Browser-19c37d?style=for-the-badge" alt="Live App"/>
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge" alt="Streamlit"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Search-minsearch-6A5ACD?style=for-the-badge" alt="minsearch"/>
</p>

<p align="center">
  <a href="https://ai-agents-dermascan.streamlit.app/" target="_blank">
    <img src="assets/hero.png" alt="DermaScan Repo Assistant" width="900"/>
  </a>
</p>

---

We'll create a conversational agent that can answer questions about any GitHub repository. Think of it as your personal AI assistant for documentation and code. If you're familiar with DeepWiki, it's similar, but tailored to your GitHub repository.

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

<img width="1608" height="1174" alt="Screenshot 2025-09-25 212832" src="https://github.com/user-attachments/assets/7d759821-550a-4307-8a86-6d87ba4d67aa" />


## Day 2 – Chunking and Intelligent Processing

📚 **Learning Log – Day 2 of AI Agents Crash Course**

Today I explored how to **prepare large documents** before sending them to an AI system.  
The focus was on **chunking** – breaking docs into smaller, meaningful pieces.

---

## What I Learned
- Large documents overwhelm LLMs (token limits, higher costs, lower performance).
- Solution: **chunking** makes docs easier to search and process.
- Different strategies give different trade-offs.

---

## Methods Implemented
1. **Sliding Window**
   - Fixed length (2000 chars) with overlap (1000 chars).  
   - Preserves continuity at boundaries.  
   - ✅ Best for most RAG pipelines.

2. **Paragraph Splitting**
   - Splits text by blank lines.  
   - Keeps natural blocks of text together.  
   - Less useful for short technical paragraphs.

3. **Section Splitting**
   - Splits by Markdown headers (`##`).  
   - Groups content logically by topics.  
   - ✅ Works well for technical docs.

4. **LLM-Based Chunking (Optional)**
   - Uses GPT or Groq models to split semantically.  
   - Produces coherent, topic-based sections.  
   - Requires API key & credits.

---

## Outputs
After running on [EvidentlyAI Docs](https://github.com/evidentlyai/docs):
- `evidently_sliding.jsonl`  
- `evidently_paragraph.jsonl`  
- `evidently_section.jsonl`  
- `evidently_llm.jsonl` *(optional)*

---

## Key Insight
✨ **Start simple.**  
Most cases work perfectly with **sliding window + overlap**.  
Advanced methods are only needed for messy or unstructured docs.

---

## Next Step
Tomorrow → **Indexing the data into a search engine** to power our AI agent. 🚀
