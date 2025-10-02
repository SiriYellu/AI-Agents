# 🩺 DermaScan Repo Assistant

This is an **AI-powered documentation assistant** built with Streamlit.  
It indexes a GitHub repository and lets you ask natural language questions like:

- *Which dataset is used and why?*  
- *What model does lesion segmentation use?*  
- *How is the Android app deployed?*  

The assistant then searches through your repo, finds the relevant context, and (optionally) uses **Gemini AI** to generate grounded answers with citations.

---

## ✨ Features
- 📥 **Repo ingestion** – automatically downloads & chunks files from GitHub.  
- 🔎 **Hybrid search** – fast lexical search using [`minsearch`](https://pypi.org/project/minsearch/).  
- 🤖 **Gemini-powered answers** – if you provide a Gemini API key.  
- 🎨 **Polished UI** – custom background, dark theme, and file badges for sources.  
- 📝 **Logging** – all Q&A are saved as JSON files in `logs/`.

---

## 🚀 Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/dermascan-agent.git
   cd dermascan-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

   You’ll see a local link like:
   ```
   http://localhost:8501
   ```

---

## 🌐 Deploy to Streamlit Cloud

1. Push your repo to GitHub.  
2. Go to [share.streamlit.io](https://share.streamlit.io/).  
3. Click **“New app”**, choose your repo, and set `app.py` as the main file.  
4. Add your Gemini API key under **Settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```
5. Done 🎉 → You’ll get a public link like:
   ```
   https://your-username-dermascan-agent.streamlit.app
   ```

---

## 📸 Screenshots (example)
*(replace with your own once deployed)*

- App Home  
  ![home screenshot](screenshots/home.png)

- Q&A Example  
  ![qa screenshot](screenshots/qa.png)

---

## 🛠 Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)  
- **Search**: [`minsearch`](https://github.com/alexeygrigorev/minsearch)  
- **LLM (optional)**: [Google Gemini](https://ai.google.dev/)  

---

## 🙌 Acknowledgements
This project was part of my **AI Agents Crash Course** journey — Day 6 (Publishing your agent).  
Thanks to the DataTalks.Club community and everyone experimenting with open-source AI tools 🚀
