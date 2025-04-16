import os
import requests
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def format_writer_prompt(user_input: dict, research_summary: str) -> str:
    topic = user_input.get("topic", "")
    subtopic = user_input.get("subtopic", "")
    draft_title = user_input.get("draft_title", "Untitled")
    keywords = user_input.get("keywords", "")
    target_audience = user_input.get("target_audience", "")
    content_goal = user_input.get("content_goal", "")
    tonality = user_input.get("tonality", "")
    structure_style = user_input.get("structure_style", "essay")
    article_length = user_input.get("article_length", "medium")
    industry_vertical = user_input.get("industry_vertical", "")
    audience_pain_points = user_input.get("audience_pain_points", "")
    geographic_focus = user_input.get("geographic_focus", "")
    reading_level = user_input.get("reading_level", "")
    reference_brands = user_input.get("reference_brands", "")
    call_to_action = user_input.get("call_to_action", "")
    include_competitors = user_input.get("include_competitors", False)

    length_map = {
        "short": 1000,
        "medium": 2000,
        "long": 3000
    }
    length_value = length_map.get(article_length, 2000)

    return f"""
You are a master content writer, blending journalistic precision and creative storytelling to craft engaging articles.

== CORE MISSION ==
Write a {structure_style}-style article on "{topic}" with a focus on "{subtopic}" that captivates {target_audience}. Achieve:
- A {tonality} voice tailored to {geographic_focus} and {industry_vertical}
- Seamless integration of {keywords} for SEO readiness
- Solutions to "{audience_pain_points}" woven into every section
- Alignment with {content_goal} to drive impact
- Emulation of {reference_brands} style (if provided)
- Readability matching {reading_level} comprehension

== STRICT LENGTH REQUIREMENTS ==
- MUST achieve {length_value} words (±10%)
- Minimum 5 H2 sections with 3-4 paragraphs each
- Each paragraph must contain 3-5 full sentences
- Failure to meet length will require full rewrite
- Word count will be verified before acceptance

== USER INPUT SUMMARY ==
- Topic: {topic}
- Subtopic: {subtopic or "N/A"}
- Draft Title: {draft_title}
- Keywords: {keywords or "N/A"}
- Target Audience: {target_audience}
- Industry Vertical: {industry_vertical or "N/A"}
- Audience Pain Points: {audience_pain_points or "N/A"}
- Geographic Focus: {geographic_focus or "Global"}
- Content Goal: {content_goal}
- Tonality: {tonality}
- Structure Style: {structure_style}
- Article Length: ~{length_value} words (STRICT)
- Reading Level: {reading_level or "Intermediate"}
- Reference Brands: {reference_brands or "None"}
- Call-to-Action: {call_to_action or "N/A"}
- Include Competitors: {"Yes" if include_competitors else "No"}

== EXPANSION TECHNIQUES ==
1. **Section Depth**:
   - Each H2 must contain:
     - 1 statistical insight from {research_summary}
     - 2 real-world examples ({geographic_focus} focused)
     - 1 extended analogy/metaphor
     - 3 {keywords} integrations

2. **Paragraph Structure**:
   - Opening: Topic sentence
   - Middle: Supporting evidence + example
   - Close: Transition to next idea

3. **Length Enforcement**:
   - If below target at 75% completion:
     - Add "Case Study" breakout boxes
     - Include 2 extra expert quotes
     - Expand all examples by 40%

== CREATIVE CONSTRAINTS ==
1. **Title Engineering**:
   - Refine "{draft_title}" into a single, engaging H1 title that:
     - Includes 1 {keywords} term
     - Addresses {audience_pain_points} or {subtopic}
     - Uses a {geographic_focus}- or {industry_vertical}-specific angle
     - Features a power verb (e.g., "Unlock," "Transform")
   - Example: For topic="{topic}", keywords="{keywords}", a title like "Unlock {keywords} Solutions for {audience_pain_points}"
   - Title must score 8/10 on clickability (test: "Would {target_audience} share this?")

2. **Introduction** (150-200 words):
   - Start with a {research_summary}-derived stat or quote tied to {topic}
   - Hook {target_audience} by addressing {audience_pain_points} in {tonality}
   - Include a "steel thread" phrase (e.g., "{subtopic} advantage") that recurs in H2/H3 headers
   - End with a promise of {content_goal}

3. **Section Development** (400-500 words each):
   - Each H2 section includes:
     - Emotional appeal to {audience_pain_points}
     - 1 data point from {research_summary}
     - 1 {geographic_focus}- or {industry_vertical}-specific example
     - 1-2 {keywords} naturally integrated
     - Subtle nod to {call_to_action}
   - Align with {content_goal} (e.g., Educate: clear steps; Persuade: counter objections)

4. **Tone and Style**:
   - Maintain {tonality} with {reading_level} complexity
   - Emulate {reference_brands} voice (e.g., conversational like Fast Company)
   - Include 1 conversational fragment per 300 words (e.g., "Sound familiar?")
   - Use 2:1 long/short paragraphs

5. **Competitor Context** (If {include_competitors}):
   - Add H2 section "How {topic} Stacks Up"
   - Use {research_summary} insights for {industry_vertical}-specific comparisons

6. **Call-to-Action**:
   - Embed {call_to_action} 3x: early H2, mid-article, conclusion
   - Tie to {audience_pain_points} organically

== OUTPUT FORMAT ==
- Return the article in markdown (## for H2, ### for H3)
- Flag 3+ {keywords}-rich phrases in <!-- -->
- Replace em dashes with hyphens ( - )
- Strictly target {length_value} words (±10%)
- No summaries or word counts
- Article will be rejected if under length
"""

def run_writer_agent(user_input: dict, research_summary: str, output_dir: str) -> dict:
    if not ANTHROPIC_API_KEY:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

    prompt = format_writer_prompt(user_input, research_summary)

    url = "https://api.anthropic.com/v1/messages"

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 8000,
        "messages": [
            {
                "role": "user",
                "content": prompt.strip()
            }
        ],
        "system": "You are a professional content writer."
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    data = response.json()
    content = data["content"][0]["text"]

    # Save writer output to output folder
    writer_path = os.path.join(output_dir, "writer.md")
    with open(writer_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

    return {
        "agent": "WriterAgent",
        "prompt": prompt.strip(),
        "article": content
    }
