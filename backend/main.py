import asyncio
import json
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

from agents.research_agent import run_research_agent
from agents.writer_agent import run_writer_agent
from agents.seo_agent import run_seo_agent
from agents.humanizer_agent import run_humanizer_agent
from agents.output_agent import get_docx_stream, sanitize_filename

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base output directory
OUTPUT_BASE_DIR = "output"
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

latest_article = ""

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_content(request: Request):
    user_input = await request.json()

    # Ensure all expected fields exist
    defaults = {
        "topic": "",
        "draft_title": "",
        "content_direction": "",
        "keywords": "",
        "target_audience": "",
        "industry_vertical": "",
        "audience_pain_points": "",
        "geographic_focus": "",
        "content_goal": "Educate",
        "tonality": "Conversational",
        "structure_style": "listicle",
        "article_length": "medium",
        "reading_level": "Intermediate",
        "reference_brands": "",
        "call_to_action": "",
        "include_competitors": True
    }
    for key, value in defaults.items():
        user_input.setdefault(key, value)

    # Create dynamic output folder: sanitized_topic_dayMonth_HHMM
    topic = user_input["topic"] or "article"
    sanitized_topic = sanitize_filename(topic)
    timestamp = datetime.now().strftime("%d%B_%H%M")
    output_dir = os.path.join(OUTPUT_BASE_DIR, f"{sanitized_topic}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    print("📡 ResearchAgent starting...")
    research_summary = run_research_agent(user_input, output_dir)["result"]

    print("✍️ WriterAgent starting...")
    raw_article = run_writer_agent(user_input, research_summary, output_dir)["article"]

    print("📈 SEOAgent starting...")
    optimized_article = run_seo_agent(user_input, raw_article, output_dir)["optimized_article"]

    print("🧠 HumanizerAgent starting...")
    final_article = run_humanizer_agent(user_input, optimized_article, research_summary, output_dir)["final_article"]

    print("📄 Generating and saving .docx file...")
    docx_stream = get_docx_stream(final_article)
    # Save DOCX to output folder
    docx_path = os.path.join(output_dir, "final.docx")
    with open(docx_path, "wb") as f:
        f.write(docx_stream.getvalue())
    # Reset stream for streaming response
    docx_stream.seek(0)

    filename = f"{sanitized_topic}_{timestamp}.docx"
    return StreamingResponse(
        docx_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/generate")
async def download_generated_article():
    global latest_article
    if not latest_article:
        return {"error": "No article available. Please generate content first."}
    
    docx_stream = get_docx_stream(latest_article)
    return StreamingResponse(
        docx_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=AutoAuthor_Article.docx"}
    )

# --- SSE Streaming Endpoint ---

import concurrent.futures

async def stream_generation(user_input: dict):
    try:
        def create_sse_payload(status: str, message: str, data: dict = None) -> dict:
            payload_content = {"status": status, "message": message}
            if data:
                payload_content.update(data)
            return {"data": json.dumps(payload_content), "event": "message"}

        # Create dynamic output folder
        topic = user_input["topic"] or "article"
        sanitized_topic = sanitize_filename(topic)
        timestamp = datetime.now().strftime("%d%B_%H%M")
        output_dir = os.path.join(OUTPUT_BASE_DIR, f"{sanitized_topic}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

        # Get the event loop and set up a thread pool
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            # Research Stage
            yield create_sse_payload("research_started", "🔍 Gathering insights from the web...")
            print("📡 ResearchAgent starting...")
            research_summary = await loop.run_in_executor(
                pool, run_research_agent, user_input, output_dir
            )
            research_summary = research_summary["result"]

            # Writing Stage
            yield create_sse_payload("writer_started", "✍️ Drafting the first cut of the article...")
            print("✍️ WriterAgent starting...")
            raw_article = await loop.run_in_executor(
                pool, run_writer_agent, user_input, research_summary, output_dir
            )
            raw_article = raw_article["article"]

            # SEO Stage
            yield create_sse_payload("seo_started", "📈 Optimizing the article...")
            print("📈 SEOAgent starting...")
            optimized_article = await loop.run_in_executor(
                pool, run_seo_agent, user_input, raw_article, output_dir
            )
            optimized_article = optimized_article["optimized_article"]

            # Humanizing Stage
            yield create_sse_payload("humanizer_started", "🧠 Adding the human touch...")
            print("🧠 HumanizerAgent starting...")
            global latest_article
            final_article = await loop.run_in_executor(
                pool, run_humanizer_agent, user_input, optimized_article, research_summary, output_dir
            )
            final_article = final_article["final_article"]
            latest_article = final_article

            # Output Stage
            yield create_sse_payload("output_started", "📄 Preparing the final document...")
            print("📄 Generating and saving .docx file...")
            docx_stream = get_docx_stream(final_article)
            docx_path = os.path.join(output_dir, "final.docx")
            with open(docx_path, "wb") as f:
                f.write(docx_stream.getvalue())

            # Completion
            yield create_sse_payload("complete", "✅ Article generated successfully!")
            print("✅ Generation complete.")

        yield {"data": json.dumps({"status": "finished", "message": "Stream closed"}), "event": "close"}

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(f"❌ Error during generation: {error_message}")
        yield {"data": json.dumps({"status": "error", "message": error_message}), "event": "error"}

async def keep_alive():
    while True:
        yield {"data": json.dumps({"status": "ping", "message": "Connection alive"}), "event": "ping"}
        await asyncio.sleep(15)

def parse_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 't', 'yes', 'y')

@app.get("/generate-stream")
async def generate_content_stream(request: Request):
    params = request.query_params
    user_input = {
        "topic": params.get("topic", ""),
        "target_audience": params.get("target_audience", ""),
        "content_goal": params.get("content_goal", "Educate"),
        "tonality": params.get("tonality", "Conversational"),
        "content_direction": params.get("content_direction", ""),
        "draft_title": params.get("draft_title", ""),
        "keywords": params.get("keywords", ""),
        "structure_style": params.get("structure_style", "listicle"),
        "article_length": params.get("article_length", "medium"),
        "include_competitors": parse_bool(params.get("include_competitors", "true")),
        "industry_vertical": params.get("industry_vertical", ""),
        "audience_pain_points": params.get("audience_pain_points", ""),
        "geographic_focus": params.get("geographic_focus", ""),
        "reading_level": params.get("reading_level", "Intermediate"),
        "reference_brands": params.get("reference_brands", ""),
        "call_to_action": params.get("call_to_action", "")
    }

    async def combined_stream():
        async for event in stream_generation(user_input):
            yield event
        async for ping in keep_alive():
            yield ping

    return EventSourceResponse(combined_stream())
