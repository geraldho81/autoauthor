import os
import requests
from dotenv import load_dotenv
from time import sleep

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar-pro"

def format_research_prompt(user_input: dict) -> str:
    topic = user_input.get("topic", "")
    content_direction = user_input.get("subtopic", "")  # Align with user_input field
    draft_title = user_input.get("draft_title", "Untitled")
    keywords = user_input.get("keywords", "")
    audience = user_input.get("target_audience", "")
    goal = user_input.get("content_goal", "")
    tone = user_input.get("tonality", "")
    structure = user_input.get("structure_style", "")
    length = user_input.get("article_length", "medium")
    vertical = user_input.get("industry_vertical", "")
    pain_points = user_input.get("audience_pain_points", "")
    geography = user_input.get("geographic_focus", "")
    level = user_input.get("reading_level", "")
    brands = user_input.get("reference_brands", "")
    call_to_action = user_input.get("call_to_action", "")
    include_competitors = user_input.get("include_competitors", False)
    
    return f"""
You are a world-class AI research assistant powered by the Perplexity API. Your role is to generate deep, multi-perspective research tailored to a user's communication goals. Go beyond surface-level summaries. Aggregate, synthesize, and structure insights from authoritative, diverse sources.

== MAIN TOPIC ==
{topic}

== SUBTOPIC ==
{content_direction if content_direction else "N/A"}

The Content directin provides specific context for the main topic. It can be a specific angle, a related concept, or a particular aspect of the main topic that the user wants to explore further. This helps narrow down the focus of the research and ensures that the insights generated are relevant to the user's needs.

== DOMAIN CONTEXT ==
- Industry Vertical: {vertical or "Not specified"}
- Geographic Focus: {geography or "None"} 
- Reading Level: {level or "General"}
- Reference Brands/Voices: {brands or "None"}

== TARGET PROFILE ==
- Audience: {audience}
- Pain Points: {pain_points or "N/A"}
- Audience Knowledge Level: Assess what this audience already knows and address knowledge gaps
- Decision-Making Factors: Consider what influences this audience's choices related to the topic

== USER OBJECTIVES ==
- Content Goal: {goal}
- Tonality: {tone}
- Structure Style: {structure}
- Desired Length: {length}
- Include Competitor Research: {"Yes" if include_competitors else "No"}

== CONTENT GOAL GUIDANCE ==
Adapt your research based on the content goal:
- Educate: Deliver structured, in-depth explanations with clarity. Prioritize factual accuracy, accessible examples, and logical progression of concepts.
- Persuade: Present compelling arguments, comparative analysis, and supporting data. Include counterarguments and address common objections with evidence.
- Entertain: Use surprising facts, witty delivery, or engaging narrative elements. Incorporate storytelling techniques and memorable anecdotes.
- Sell: Focus on benefits, differentiation, and persuasive positioning. Highlight value propositions and include credibility elements such as social proof or authority references.
- Inspire: Highlight emotionally resonant stories or visionary thinking. Connect to larger themes and include aspirational elements that resonate with audience values.
- Awareness: Offer accessible and well-explained facts. Prioritize clear explanations of key concepts with relevant current context.
- Engage: Present thought-provoking content that sparks curiosity or discussion. Include conversation starters and perspectives that challenge conventional thinking.

== RESEARCH METHODOLOGY ==
1. Identify and prioritize authoritative sources from:
   - Academic research and peer-reviewed journals
   - Industry reports and whitepapers
   - Expert opinions and thought leadership
   - Statistical databases and market analyses
   - Primary sources when available
2. Apply triangulation by cross-referencing multiple sources
3. Note areas of consensus, disagreement, and emerging perspectives
4. Distinguish between established facts, expert opinions, and emerging trends
5. Consider temporal relevance (historical context and current developments)

== ANALYTICAL FRAMEWORK ==
- Compare and contrast multiple perspectives on the topic
- Identify underlying assumptions in different viewpoints
- Apply appropriate theoretical frameworks relevant to the topic
- Consider implications and practical applications of research findings
- Evaluate strength of evidence behind key claims
- Highlight knowledge gaps or areas requiring further research

== TASK ==
1. Deeply research the main topic, providing contextual background and current relevance
2. Enrich with the subtopic where applicable, showing relationships between main topic and subtopic
3. Align insights with the target audience and their pain points, using appropriate language and examples
4. Format insights in a style that matches the specified structure and tone
5. If competitor analysis is requested, include market comparisons, positioning strategies, and competitive advantages/disadvantages
6. Integrate specific data points, statistics, and concrete examples to support key points
7. Present balanced perspectives that acknowledge complexity and nuance
8. Conclude with actionable implications or forward-looking insights

Only return structured, insightful, and synthesized research – no fluff. Prioritize depth over breadth, focusing on the most relevant aspects for the specified audience and content goal.
"""

def run_research_agent(user_input: dict, output_dir: str) -> dict:
    if not PERPLEXITY_API_KEY:
        raise EnvironmentError("PERPLEXITY_API_KEY not set in .env")

    prompt = format_research_prompt(user_input)

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt.strip()}],
        "temperature": 0.7,
        "max_tokens": 10240,
        "top_p": 0.9
    }

    MAX_RETRIES = 3
    RETRY_DELAY = 1.5

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or not data["choices"]:
                raise ValueError("Unexpected API response structure")

            content = data["choices"][0]["message"]["content"]
            # Save research summary to output folder
            research_path = os.path.join(output_dir, "research.txt")
            with open(research_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

            return {
                "agent": "ResearchAgent",
                "prompt": prompt.strip(),
                "result": content.strip()
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limited. Retrying in {RETRY_DELAY ** (attempt + 1)} seconds...")
                sleep(RETRY_DELAY ** (attempt + 1))
                continue
            print(f"[ResearchAgent] HTTP Error: {e.response.text}")
            raise

        except KeyError:
            print("[ResearchAgent] Malformed API response")
            raise
