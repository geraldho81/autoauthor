import asyncio
import json
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate")
async def generate_content(request: Request):
    user_input = await request.json()

    print("📡 ResearchAgent starting...")
    research_summary = run_research_agent(user_input)["result"]

    print("✍️ WriterAgent starting...")
    raw_article = run_writer_agent(user_input, research_summary)["article"]

    print("📈 SEOAgent starting...")
    optimized_article = run_seo_agent(user_input, raw_article)["optimized_article"]

    print("🧠 HumanizerAgent starting...")
    final_article = run_humanizer_agent(user_input, optimized_article)["final_article"]

    print("📄 Streaming .docx file to user...")
    docx_stream = get_docx_stream(final_article)
    filename = sanitize_filename(user_input["draft_title"]) + ".docx"

    return StreamingResponse(
        docx_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# --- SSE Streaming Endpoint ---

async def stream_generation(user_input: dict):
    try:
        def create_sse_payload(status: str, message: str, data: dict = None) -> dict:
            payload_content = {"status": status, "message": message}
            if data:
                payload_content.update(data)
            return {"data": json.dumps(payload_content)}

        yield create_sse_payload("research_started", "🔍 Gathering insights from the web...")
        print("📡 ResearchAgent starting...")
        research_summary = run_research_agent(user_input)["result"]

        yield create_sse_payload("writer_started", "✍️ Drafting the first cut of the article...")
        print("✍️ WriterAgent starting...")
        raw_article = run_writer_agent(user_input, research_summary)["article"]

        yield create_sse_payload("seo_started", "📈 Optimizing the article...")
        print("📈 SEOAgent starting...")
        optimized_article = run_seo_agent(user_input, raw_article)["optimized_article"]

        yield create_sse_payload("humanizer_started", "🧠 Adding the human touch...")
        print("🧠 HumanizerAgent starting...")
        final_article = run_humanizer_agent(user_input, optimized_article)["final_article"]

        yield create_sse_payload("output_started", "📄 Preparing the final document...")
        print("📄 OutputAgent skipped file save — using stream.")

        yield create_sse_payload("complete", "✅ Article generated successfully!")
        print("✅ Generation complete.")

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(f"❌ Error during generation: {error_message}")
        yield {"data": json.dumps({"status": "error", "message": f"❌ {error_message}"})}

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
        "subtopic": params.get("subtopic", ""),
        "draft_title": params.get("draft_title", ""),
        "keywords": params.get("keywords", ""),
        "structure_style": params.get("structure_style", "listicle"),
        "article_length": params.get("article_length", "medium"),
        "include_competitors": parse_bool(params.get("include_competitors", "true"))
    }
    return EventSourceResponse(stream_generation(user_input))
