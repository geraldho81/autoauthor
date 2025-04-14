import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def format_writer_prompt(user_input: dict, research_summary: str) -> str:
    title = user_input.get("draft_title", "Untitled")
    audience = user_input.get("target_audience", "")
    tone = user_input.get("tonality", "")
    goal = user_input.get("content_goal", "")
    structure = user_input.get("structure_style", "essay")
    length = user_input.get("article_length", "medium ~2000 words")

    # 🔁 Map display value to numeric word estimate
    length_map = {
        "short ~1000 words": 1000,
        "medium ~2000 words": 2000,
        "long ~3000 words": 3000
    }
    length_value = length_map.get(length, 2000)  # Default to 2000 words

    return f"""
You are a professional content writer.

Write a structured article based on the research summary below and the user brief.

== User Brief ==
- Title: {title}
- Target Audience: {audience}
- Tone: {tone}
- Goal: {goal}
- Structure Style: {structure}
- Article Length: {length} (~{length_value} words)

== Research Summary ==
{research_summary}

== Instructions ==
1. Begin with a TL;DR summary (2–3 lines).
2. Follow with a full article using H1 for title, H2 for sections, and H3 for subpoints.
3. Use natural language, practical examples, and varied sentence structure.
4. Match the tone and goal. Do not sound robotic or generic.
5. The article must be approximately {length_value} words in length — not characters or tokens.
"""

def run_writer_agent(user_input: dict, research_summary: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    prompt = format_writer_prompt(user_input, research_summary)

    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional content writer."},
            {"role": "user", "content": prompt.strip()}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return {
        "agent": "WriterAgent",
        "prompt": prompt.strip(),
        "article": content
    }
