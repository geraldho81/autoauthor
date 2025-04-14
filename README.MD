# 🧠 AutoAuthor

AutoAuthor is an intelligent content generation system that transforms your input brief into a fully-researched, SEO-optimized, humanized article, saved as a Word document.

## ✅ Key Features

*   🔍 Research Agent – Gathers real-time insights from the web.
*   ✍️ Writer Agent – Drafts a complete article based on your input.
*   📈 SEO Agent – Optimizes the article based on SEO best practices.
*   🧠 Humanizer Agent – Makes the article sound natural and human.
*   📄 Output Agent – Saves the article as a clean .docx file in the `output/` folder.

## 🖥️ Tech Stack

*   Backend: FastAPI (Python)
*   Frontend: Basic HTML/JavaScript
*   Agents: Modular Python scripts
*   LLMs Used: Perplexity, DeepSeek, Claude (optional)

## 📦 Folder Structure

```
autoauthor/
├── backend/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── writer_agent.py
│   │   ├── seo_agent.py
│   │   ├── humanizer_agent.py
│   │   └── output_agent.py
│   ├── main.py
│   └── requirements.txt
├── frontend/       # Basic HTML/JavaScript UI
│   └── index.html
├── output/         # Final articles saved as .docx
├── .env            # Your API keys
└── run_autoauthor.command # Mac launch shortcut (optional)
```

## 🧪 How to Use

1.  **🔧 Set up the backend:**

    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **🔑 Add your API keys:**

    Create a `.env` file in the `backend/` folder:

    ```ini
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxx
    DEEPSEEK_API_KEY=ds-xxxxxxxxxxxxxxxx
    CLAUDE_API_KEY=claude-xxxxxxxxxxxxxxxx  # Optional
    ```

3.  **🚀 Run the app:**

    *   Backend (FastAPI):

        ```bash
        cd backend
        source venv/bin/activate
        uvicorn main:app --reload
        ```

    *   Frontend: Open `frontend/index.html` in your browser (the `run_autoauthor.command` script does this automatically).

## 🧠 How It Works

1.  You fill out the form in `frontend/index.html`: topic, audience, tone, keywords, etc.
2.  Click "Generate Article". The UI will display "Your article is now being created, please wait for a moment..."
3.  The system runs a chain of agents on the backend:
    *   ResearchAgent
    *   WriterAgent
    *   SEOAgent
    *   HumanizerAgent
    *   OutputAgent
4.  When the process is complete, the UI will update with a success message and the path to your `.docx` file, which is saved in the `output/` directory.