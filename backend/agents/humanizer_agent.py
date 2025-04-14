import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def format_deepseek_prompt(user_input: dict, seo_article: str) -> str:
    tone = user_input.get("tonality", "")
    audience = user_input.get("target_audience", "")
    goal = user_input.get("content_goal", "")
    structure = user_input.get("structure_style", "")
    length = user_input.get("article_length", "")

    # Map label to numeric word count
    length_map = {
        "short ~1000 words": 1000,
        "medium ~2000 words": 2000,
        "long ~3000 words": 3000
    }
    length_value = length_map.get(length, 2000)  # Default to 2000 if unspecified

    # Replace em dashes with hyphen + space
    seo_article = seo_article.replace("—", " - ")

    return f"""
You are a human content specialist.

Your task is to humanize and refine the following SEO-optimized article. Make it emotionally resonant, readable, and natural — but don't lose structure or SEO.

== User Brief ==
- Tone: {tone}
- Audience: {audience}
- Goal: {goal}
- Structure: {structure}
- Target Length: {length} (~{length_value} words)

== Rules ==
1. DO NOT use em dashes (—). Replace them with hyphens with spaces ( - ) instead.
2. DO NOT add any commentary, summaries, sign-offs, or meta descriptions outside the article.
3. DO NOT include the word count in the output.
4. Keep SEO keywords and formatting intact.
5. Fix robotic transitions, flat phrasing, and repetition.
6. Use a tone that suits the audience and intent.
7. Aim for approximately {length_value} words in content. DO NOT include the word count in the output.
8. Output should be clean, with markdown-style H1, H2, H3 headers.
9. Output ONLY the final humanized article. No prefaces, no explanations, no extra text.

== Article ==
{seo_article}

Only return the humanized article text. Do not include any additional explanations, summaries, or word count.
"""

def run_humanizer_agent(user_input: dict, seo_article: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    prompt = format_deepseek_prompt(user_input, seo_article)

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt.strip()}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    result = response.json()["choices"][0]["message"]["content"]

    # Optional: Remove lingering "word count" notes if model still slips up
    result = re.sub(r"\(?(word count|~?\s*\d+\s*words)\)?", "", result, flags=re.IGNORECASE)

    return {
        "agent": "HumanizerAgent",
        "prompt": prompt.strip(),
        "final_article": result.strip()
    }
