import os
import requests
from dotenv import load_dotenv
from time import sleep

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar"  # Adjust model name if needed

def format_research_prompt(user_input: dict) -> str:
    topic = user_input.get("topic", "")
    audience = user_input.get("target_audience", "")
    goal = user_input.get("content_goal", "")
    tone = user_input.get("tonality", "")
    subtopic = user_input.get("subtopic", "")
    structure = user_input.get("structure_style", "")
    length = user_input.get("article_length", "medium")

    return f"""
You are a world-class AI research assistant powered by the Perplexity API. Your role is to generate deep, multi-perspective research tailored to a user’s communication goals. You will be provided with a primary topic and a set of contextual parameters. Your task is to go beyond surface-level information by aggregating, synthesizing, and structuring insights from authoritative and diverse sources.

== MAIN TOPIC ==
{topic}

== SUBTOPIC ==
{subtopic if subtopic else "N/A"}

The user may also include a subtopic, which is a secondary but related concept or theme. Use this to enrich the depth and breadth of your research — it may serve as a complementary angle, additional context, or expansion point to the main topic.

Research the main topic deeply, prioritizing accuracy, nuance, and synthesis of ideas from multiple high-authority sources.

Integrate the Subtopic as a complementary theme that supports or expands on the main topic. Use it to provide additional depth, contrast, case examples, or secondary insights where appropriate.

== USER BRIEF ==
- Target Audience: {audience}
- Content Goal: {goal}
- Tonality: {tone}
- Structure Style: {structure}
- Article Length: {length}

== CONTENT GOAL GUIDANCE ==
Adapt your research to match the goal:
- Educate: Deliver structured, in-depth explanations with clarity.
- Persuade: Present compelling arguments, comparative analysis, and supporting data.
- Entertain: Use surprising facts, witty delivery, or engaging narrative elements.
- Sell: Focus on benefits, differentiation, and persuasive positioning.
- Inspire: Highlight emotionally resonant stories or visionary thinking.
- Awareness: Offer accessible and well-explained facts.
- Engage: Present thought-provoking content that sparks curiosity or discussion.

Adapt research insights to suit the target audience, factoring in their knowledge level, interests, and intent. Match the selected tonality in style, vocabulary, and structure. Use the specified structure style to organize the research in a format that best serves the user’s objective.

Output should be accurate, rich in synthesis, and highly useful.
"""

def run_research_agent(user_input: dict) -> dict:
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
