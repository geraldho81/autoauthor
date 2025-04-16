import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def format_deepseek_prompt(user_input: dict, seo_article: str, research_summary: str) -> str:
    tone = user_input.get("tonality", "")
    content_direction = user_input.get("content_direction", "")
    audience = user_input.get("target_audience", "")
    goal = user_input.get("content_goal", "")
    structure = user_input.get("structure_style", "")
    length = user_input.get("article_length", "")
    vertical = user_input.get("industry_vertical", "")
    pain_points = user_input.get("audience_pain_points", "")
    geography = user_input.get("geographic_focus", "")
    level = user_input.get("reading_level", "")
    brands = user_input.get("reference_brands", "")
    call_to_action = user_input.get("call_to_action", "")
    include_competitors = user_input.get("include_competitors", False)

    length_map = {
        "short ~1000 words": 1000,
        "medium ~2000 words": 2000,
        "long ~3000 words": 3000
    }
    length_value = length_map.get(length, 2000)

    # Clean up em dashes
    seo_article = seo_article.replace("—", " - ")
    research_summary = research_summary.replace("—", " - ")

    return f"""
You are a human content specialist.

Your job is to humanize the following SEO-optimized article. Make it emotionally resonant, readable, and natural – but do not lose structure, formatting, or SEO value.

== USER BRIEF ==
- Title: {user_input.get("draft_title", "Untitled")}
- Content Direction: {content_direction or "N/A"}
- Industry: {vertical}
- Audience: {audience}
- Known Pain Points: {pain_points}
- Geography: {geography}
- Reading Level: {level}
- Tone: {tone}
- Goal: {goal}
- Structure Style: {structure}
- Reference Brands: {brands or "N/A"}
- Include Competitors: {"Yes" if include_competitors else "No"}
- Suggested CTA: {call_to_action or "N/A"}
- Target Length: {length} (~{length_value} words)

== CONTEXTUAL REFERENCE ==
Use both the original research summary and the current draft article as background to guide tone, flow, and content alignment. You may draw upon ideas, examples, or narrative flow elements from either if they help humanize the content effectively.

== RESEARCH SUMMARY ==
{research_summary}

== ARTICLE TO HUMANIZE ==
{seo_article}

== HUMANIZATION RULES ==
1. DO NOT use em dashes (—). Replace with spaced hyphens ( - ).
2. DO NOT add summaries, prefaces, sign-offs, or meta-descriptions.
3. DO NOT include word counts in the final output.
4. Preserve SEO keywords and header formatting (H1, H2, H3 in markdown).
5. Eliminate robotic transitions, filler phrases, or overly flat structure.
6. Adjust the voice to match the tone, audience pain points, and brand inspiration.
7. Ensure a natural flow and conversational rhythm.
8. Keep the message focused and relevant to the audience's knowledge level and needs. 
9. Ensure that the article aligns with the content direction

== OUTPUT FORMAT ==
Only return the humanized article using markdown-style formatting. DO NOT wrap the output in a code block (e.g., ```markdown). DO NOT include any commentary or extra explanation.
"""

def run_humanizer_agent(user_input: dict, seo_article: str, research_summary: str, output_dir: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    prompt = format_deepseek_prompt(user_input, seo_article, research_summary)

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

    # Clean up any accidental word count mentions
    result = re.sub(r"\(?(word count|~?\s*\d+\s*words)\)?", "", result, flags=re.IGNORECASE)

    # Clean up markdown code block delimiters if present
    result = re.sub(r'^```markdown\s*\n', '', result, flags=re.MULTILINE)  # Remove starting ```markdown
    result = re.sub(r'\n```$', '', result, flags=re.MULTILINE)  # Remove ending ```
    result = result.strip()  # Remove any leading/trailing whitespace

    # Save humanizer output to output folder
    humanizer_path = os.path.join(output_dir, "humanizer.md")
    with open(humanizer_path, "w", encoding="utf-8") as f:
        f.write(result.strip())

    return {
        "agent": "HumanizerAgent",
        "prompt": prompt.strip(),
        "final_article": result.strip()
    }
