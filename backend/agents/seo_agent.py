import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def format_seo_prompt(user_input: dict, draft_article: str) -> str:
    keywords = user_input.get("keywords", "")
    tone = user_input.get("tonality", "")
    audience = user_input.get("target_audience", "")
    goal = user_input.get("content_goal", "")
    style = user_input.get("structure_style", "")
    length = user_input.get("article_length", "")

    # Map dropdown label to actual word count estimate
    length_map = {
        "short ~1000 words": 1000,
        "medium ~2000 words": 2000,
        "long ~3000 words": 3000
    }
    length_value = length_map.get(length, 2000)  # Default to 2000 words if unmatched

    return f"""You are an expert SEO content optimizer.

Your task is to improve the following article using these SEO guidelines:

== SEO Guidelines ==
1. Insert main and related keywords naturally: {keywords}
2. Improve content depth (clarify weak points, add examples).
3. Structure headings properly (H1 for title, H2 for sections, H3 for subpoints).
4. Improve readability: vary sentence length, avoid robotic phrasing, aim for Flesch score > 60.
5. Align with Google's Helpful Content Guidelines:
   - Human-first, not keyword-stuffed
   - Answer real user queries clearly
   - Provide unique and helpful insights
6. Apply EEAT principles:
   - Experience (real examples)
   - Expertise (accurate terminology)
   - Authority (cite relevant tools or stats)
   - Trustworthiness (neutral, informative tone)

== User Brief ==
- Audience: {audience}
- Goal: {goal}
- Tone: {tone}
- Structure Style: {style}
- Expected Length: {length} (~{length_value} words)

== Length Note ==
The optimized article must retain or expand to approximately {length_value} **words** — not characters or tokens.

== Article to Optimize ==
{draft_article}

== Output Instructions ==
- Return only the improved article
- Maintain markdown formatting (H1, H2, etc.)
- Do not remove original ideas — only enhance
"""

def run_seo_agent(user_input: dict, draft_article: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    prompt = format_seo_prompt(user_input, draft_article)

    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are an expert SEO content editor."},
            {"role": "user", "content": prompt.strip()}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return {
        "agent": "SEOAgent",
        "prompt": prompt.strip(),
        "optimized_article": content
    }
