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



<!-- ====== QUICK DEMO ====== -->

## 🎥 Quick Demo

<!-- Preferred: use a short GIF for inline playback on GitHub -->
<p align="center">
  <img src="
<!-- ====== QUICK DEMO ====== -->

## 🎥 Quick Demo

<!-- Preferred: use a short GIF for inline playback on GitHub -->
<p align="center">
  <img src="assets/Screen Recording 2025-10-02 024934.gif" alt="DermaScan Demo GIF" width="900"/>
</p>

## 📸 Screenshots
<img width="2047" height="1050" alt="Screenshot 2025-10-02 020507" src="https://github.com/user-attachments/assets/2ee84a55-e5b6-46cd-bed3-88b4695e90a7" />

<img width="2047" height="1070" alt="Screenshot 2025-10-02 025140" src="https://github.com/user-attachments/assets/fe7f2e15-f557-49dc-93e8-4313d832135a" />

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
Tomorrow → **Indexing the data into a search engine** to power our AI agent. 

##  Day 3 — Indexing & Search
**What I Learned:**  
- How to chunk repo files and index them for efficient search.  

**Methods Implemented:**  
- Used `minsearch` lexical index with sliding window + stride.  
- Parsed `.java`, `.kt`, `.xml`, `.py`, and `.md` files from repo.  

**Outputs:**  
- Search tool returning top-k relevant file chunks.  
- Verified with sanity-check queries.  

**Key Insight:**  
- A good index is the foundation for an accurate repo Q&A agent.  

**Next Step:**  
- Connect search results with an LLM for grounded answers.  

---

##  Day 4 — Agent Creation
**What I Learned:**  
- How to connect LLM reasoning with repo search context.  

**Methods Implemented:**  
- Created agent with system prompt enforcing “answer only from repo”.  
- Integrated search results into prompt.  

**Outputs:**  
- First working repo Q&A agent (CLI).  
- Returned answers citing file snippets.  

**Key Insight:**  
- Without grounding, LLMs hallucinate — retrieval drastically improves trust.  

**Next Step:**  
- Evaluate systematically with structured questions and auto-grading.  

---

##  Day 5 — Evaluation
**What I Learned:**  
- Importance of quantitative evaluation for agent reliability.  

**Methods Implemented:**  
- Logged interactions into JSON.  
- Added LLM-as-a-Judge evaluation pipeline.  
- Generated test questions automatically from repo docs.  

**Outputs:**  
- Metrics on correctness, citation quality, clarity.  
- Evaluation reports for multiple runs.  

**Key Insight:**  
- Logging + evals close the loop between “demo” and “measurable progress.”  

**Next Step:**  
- Build a UI for others to interact with the agent easily.  

---

##  Day 6 — UI & Deployment
**What I Learned:**  
- How to serve AI agents via a web interface.  

**Methods Implemented:**  
- Built Streamlit chat app with history + styling.  
- Added background image and custom CSS.  
- Enabled Gemini integration (with lexical fallback).  

**Outputs:**  
- Interactive app answering repo questions.  
- Deployed publicly on Streamlit Cloud.  
