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

