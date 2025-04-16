AutoAuthor
AutoAuthor is an AI-powered content generation tool that transforms a user-provided brief into a well-researched, SEO-optimized, and humanized article, delivered as a downloadable Word document.
✨ Key Features

🔍 Research Agent: Collects real-time insights using the Perplexity API.
✍️ Writer Agent: Crafts a detailed article based on your input and research.
📈 SEO Agent: Enhances the article for search engine visibility using DeepSeek.
🧠 Humanizer Agent: Refines the article to sound natural and engaging.
📄 Output Agent: Converts the final article into a .docx file, saved on the server and downloadable.

🖥️ Tech Stack

Backend: FastAPI (Python)
Frontend: HTML, JavaScript, Bootstrap
Agents: Modular Python scripts
APIs: Perplexity (research), DeepSeek (SEO, humanization), Anthropic Claude (Creative Writing)
Dependencies: See backend/requirements.txt

📂 Project Structure
autoauthor/
├── backend/                    # Server-side code
│   ├── agents/                 # Agent scripts
│   │   ├── research_agent.py
│   │   ├── writer_agent.py
│   │   ├── seo_agent.py
│   │   ├── humanizer_agent.py
│   │   └── output_agent.py
│   ├── main.py                 # FastAPI app
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Client-side UI
│   └── index.html              # Form and progress UI
├── output/                     # Generated .docx files and intermediate outputs
├── .env                        # API keys (not in repo)
└── run_autoauthor.command      # Optional Mac launch script

🧪 Getting Started
Prerequisites

Python 3.8+
API keys for Perplexity and DeepSeek (Anthropic Claude optional)
A modern web browser

Installation

Clone the Repository:
git clone https://github.com/your-repo/autoauthor.git
cd autoauthor


Set Up the Backend:
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Configure API Keys: Create a .env file in the backend/ directory with your API keys:
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxx
DEEPSEEK_API_KEY=ds-xxxxxxxxxxxxxxxx
CLAUDE_API_KEY=claude-xxxxxxxxxxxxxxxx  # Optional



Running the App

Start the Backend:
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000

The API will be available at http://localhost:8000.

Access the Frontend:

Open frontend/index.html in a browser (e.g., drag the file into Chrome).
Alternatively, use the run_autoauthor.command script on macOS to launch the frontend and backend together (ensure the backend is running first).



Usage

Open http://localhost:8000 (or the frontend file) in your browser.
Fill out the form with details like topic, target audience, tone, keywords, etc.
Click Generate Article to start the process.
Watch the progress bar for real-time updates (e.g., "Researching," "Drafting").
Once complete, download the .docx file via the provided link. The file is also saved in the output/ directory on the server.

Cleaning Up
Generated files are stored in the output/ directory. To free up server space:
cd output
rm -rf *

Or delete the entire directory:
rm -rf output

The app will recreate the output/ directory as needed.
🧠 How It Works

User Input: You provide a brief via the form in index.html, specifying topic, audience, tone, etc.
Agent Pipeline:
Research Agent: Gathers insights using Perplexity API.
Writer Agent: Drafts the article based on research and user input.
SEO Agent: Optimizes for SEO with DeepSeek, preserving structure.
Humanizer Agent: Refines the tone to sound natural and engaging.
Output Agent: Converts the article to a .docx file, saved in output/ and streamed for download.


Progress Updates: The frontend displays real-time status via Server-Sent Events (SSE).
Output: A .docx file is generated, downloadable via the UI and stored on the server.

⚠️ Notes for Public Deployment

Concurrency: The app uses a global latest_article variable, so simultaneous generations may cause users to download incorrect files. For a showcase, ensure sequential usage (one user at a time).
Storage: The output/ directory grows with each generation. Manually clear it post-showcase to manage disk space.
API Limits: Ensure your Perplexity and DeepSeek API keys have sufficient quotas for demo usage.

🛠️ Troubleshooting

API Errors: Check .env for correct API keys and verify quotas.
Progress Bar Lag: Ensure the backend uses the updated stream_generation function with ThreadPoolExecutor (already fixed).
Download Issues: If users get the wrong file, avoid concurrent generations or download immediately after generation.

📜 License
MIT License. Feel free to use, modify, and share!
