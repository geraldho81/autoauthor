import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse # Keep for original endpoint if needed
from sse_starlette.sse import EventSourceResponse # Import specific SSE response
from fastapi.middleware.cors import CORSMiddleware

from agents.research_agent import run_research_agent
from agents.writer_agent import run_writer_agent
from agents.seo_agent import run_seo_agent
from agents.humanizer_agent import run_humanizer_agent
from agents.output_agent import run_output_agent
app = FastAPI()

# Allow CORS for frontend access
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

# Original endpoint (kept for potential direct use/testing)
@app.post("/generate")
async def generate_content(request: Request):
    user_input = await request.json()

    print("📡 ResearchAgent starting...")
    research_output = run_research_agent(user_input)
    research_summary = research_output["result"]

    print("✍️ WriterAgent starting...")
    writer_output = run_writer_agent(user_input, research_summary)
    raw_article = writer_output["article"]

    print("📈 SEOAgent starting...")
    seo_output = run_seo_agent(user_input, raw_article)
    optimized_article = seo_output["optimized_article"]

    print("🧠 HumanizerAgent starting...")
    human_output = run_humanizer_agent(user_input, optimized_article)
    final_article = human_output["final_article"]

    print("📄 OutputAgent running...")
    output_result = run_output_agent(final_article, user_input["draft_title"])

    return {
        "status": "success",
        "final_article_markdown": output_result.get("markdown", ""), # Use .get for safety
        "docx_file_path": output_result.get("docx_file_path", ""),
        "html_preview": output_result.get("html", "")
    }

# --- SSE Streaming Endpoint ---

async def stream_generation(user_input: dict):
    """Generator function to stream agent progress via SSE."""
    try:
        # Helper to create the payload dictionary for SSE messages
        # Helper to create the payload dictionary for SSE messages
        # EventSourceResponse expects the actual data under a 'data' key,
        # which it will then JSON encode.
        def create_sse_payload(status: str, message: str, data: dict = None) -> dict:
            payload_content = {"status": status, "message": message}
            if data:
                payload_content.update(data)
            # Wrap the content in the structure EventSourceResponse expects
            return {"data": json.dumps(payload_content)}

        # --- Agent Execution Sequence ---
        # EventSourceResponse expects dictionaries, not formatted strings

        # Research Agent
        yield create_sse_payload("research_started", "🔍 Gathering insights from the web...")
        print("📡 ResearchAgent starting...")
        research_output = run_research_agent(user_input) # Sync call
        research_summary = research_output["result"]
        # No intermediate complete message needed

        # Writer Agent
        yield create_sse_payload("writer_started", "✍️ Drafting the first cut of the article...")
        print("✍️ WriterAgent starting...")
        writer_output = run_writer_agent(user_input, research_summary) # Sync call
        raw_article = writer_output["article"]
        # No intermediate complete message needed

        # SEO Agent
        yield create_sse_payload("seo_started", "📈 Optimizing the article...")
        print("📈 SEOAgent starting...")
        seo_output = run_seo_agent(user_input, raw_article) # Sync call
        optimized_article = seo_output["optimized_article"]
        # No intermediate complete message needed

        # Humanizer Agent
        yield create_sse_payload("humanizer_started", "🧠 Adding the human touch...")
        print("🧠 HumanizerAgent starting...")
        human_output = run_humanizer_agent(user_input, optimized_article) # Sync call
        final_article = human_output["final_article"]
        # No intermediate complete message needed

        # Output Agent
        yield create_sse_payload("output_started", "📄 Preparing the final document...")
        print("📄 OutputAgent running...")
        output_result = run_output_agent(final_article, user_input["draft_title"]) # Sync call
        # No intermediate complete message needed

        # Final success message
        yield create_sse_payload("complete", "✅ Article generated successfully!", data={
            "docx_file_path": output_result.get("docx_file_path", ""),
        })
        print("✅ Generation complete.")


    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(f"❌ Error during generation: {error_message}")
        # Ensure error message is also sent in the correct format
        yield {"data": json.dumps({"status": "error", "message": f"❌ {error_message}"})}

# Removed sse_wrapper as it's not needed with correct generator structure

# Helper function to parse boolean query parameters
def parse_bool(value: str) -> bool:
    return value.lower() in ('true', '1', 't', 'yes', 'y')

@app.get("/generate-stream") # Changed from POST to GET
async def generate_content_stream(request: Request):
    # Read data from query parameters instead of JSON body
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
    # Use EventSourceResponse for proper SSE handling
    return EventSourceResponse(stream_generation(user_input))
