import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def format_seo_prompt(user_input: dict, draft_article: str) -> str:
    title = user_input.get("draft_title", "Untitled")
    content_direction = user_input.get("content_direction", "")
    keywords = user_input.get("keywords", "")
    audience = user_input.get("target_audience", "")
    tone = user_input.get("tonality", "")
    goal = user_input.get("content_goal", "")
    structure = user_input.get("structure_style", "essay")
    length = user_input.get("article_length", "medium ~2000 words")
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

    return f"""You are an expert SEO content optimizer.

Your task is to improve the following article using advanced SEO techniques and user-aligned strategy.

== SEO STRATEGY ==
1. Integrate primary and related keywords naturally: {keywords}
2. Add relevant internal and external references if suitable
3. Improve structure using proper headers (H1 for title, H2/H3 for sections)
4. Enhance clarity, depth, and examples — especially for audience pain points
5. Maintain tone: {tone}, and reflect reader expectations
6. Aim for Flesch Reading Ease > 60
7. Avoid robotic or generic phrasing

== EEAT + HELPFUL CONTENT PRINCIPLES ==
- Experience: Add real examples or context
- Expertise: Use accurate terms and trusted references
- Authority: Mention brands, tools, or frameworks where relevant
- Trust: Neutral, accessible, honest tone
- Helpfulness: Focus on solving real reader queries

== USER BRIEF ==
- Industry: {vertical}
- Audience: {audience}
- Known Pain Points: {pain_points}
- Geography: {geography}
- Reading Level: {level}
- Structure Style: {structure}
- Goal: {goal}
- Tone: {tone}
- Brands to Match: {brands}
- Include Competitor Context: {"Yes" if include_competitors else "No"}
- Suggested CTA: {call_to_action or "N/A"}

== LENGTH ==
Target length is approximately {length_value} words. Retain or expand only if valuable — no padding.

== ARTICLE TO OPTIMIZE ==
{draft_article}

== OUTPUT FORMAT ==
- Return only the optimized article
- Keep markdown formatting (## for H2, ### for H3, etc.)
- Do NOT remove original ideas — only improve them
"""

def run_seo_agent(user_input: dict, draft_article: str, output_dir: str) -> dict:
    if not DEEPSEEK_API_KEY:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    prompt = format_seo_prompt(user_input, draft_article)

    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "You are an expert SEO content editor."},
            {"role": "user", "content": prompt.strip()}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Save SEO output to output folder
    seo_path = os.path.join(output_dir, "seo.md")
    with open(seo_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

    return {
        "agent": "SEOAgent",
        "prompt": prompt.strip(),
        "optimized_article": content
    }
