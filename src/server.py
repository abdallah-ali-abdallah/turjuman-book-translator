# This file sets up the Langserve server for the compiled LangGraph application.

from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime
load_dotenv() # Load environment variables from .env file

# --- Setup file logger ---
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"server_log_{timestamp}.log")

file_handler = logging.FileHandler(log_file, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger("turjuman")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Optional: also log to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger.info(f"Server started, logging to {log_file}")

from .providers import list_available_providers
list_available_providers()  # Print available providers/models at startup

from fastapi import FastAPI, Request, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse, Response
import json
import asyncio
import threading
import queue
import copy
from . import graph
from .state import TranslationState
from .utils import update_progress
from fastapi.responses import HTMLResponse, FileResponse # Add FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from langserve import add_routes
from langchain_core.callbacks import BaseCallbackHandler

# Import database and worker modules
from .database import init_db
from .job_queue import JobQueue
from .worker import TranslationWorker

# Initialize job queue and worker
job_queue = JobQueue()
worker = TranslationWorker()


try:
    from .graph import app as langgraph_app # Use relative import
    from .state import TranslationState     # Use relative import
except ImportError:
    from .graph import app as langgraph_app # Use relative import
    from .state import TranslationState     # Use relative import

# --- FastAPI App Setup ---
# Add metadata for API docs
app = FastAPI(
    title="LangGraph Translation Server",
    version="1.0",
    description="API Server for the LangGraph-based Document Translation Workflow. Provides endpoints to manage and track translation jobs.",
)

# --- Initialize database and start worker on startup ---
@app.on_event("startup")
async def startup_event():
    """Initialize database and start worker on startup."""
    await init_db()
    
    # Load environment variables from database
    from .database import load_env_variables_to_os, sync_env_file_with_db, get_default_llm_config
    
    # First sync .env file with database (for first run)
    await sync_env_file_with_db()
    
    # Then load variables from database to os.environ
    await load_env_variables_to_os()
    
    # Start worker in background
    asyncio.create_task(worker.start())
    
    # Log default LLM config if available
    default_config = await get_default_llm_config()
    if default_config:
        logger.info(f"Default LLM configuration loaded: {default_config['provider']} - {default_config['model']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop worker on shutdown."""
    await worker.stop()

# --- Mount Frontend Static Files ---
# Assumes frontend files are in ../frontend relative to this file (src/server.py)
# Dockerfile should ensure this structure is present in the container.
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Serve static assets (JS, CSS, images) from /static path prefix
# The 'directory' path MUST exist at runtime.
# Check=False prevents FastAPI from raising an error if the dir doesn't exist at startup,
# which might be useful in some deployment scenarios, but generally it should exist.
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="frontend_static")
    logger.info(f"Serving static files from {frontend_dir} at /static")
else:
    logger.warning(f"Frontend directory {frontend_dir} not found. Static files will not be served.")


# --- Add Route for index.html at root ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend_app():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.error(f"index.html not found at {index_path}")
        # Fallback if index.html isn't found
        return HTMLResponse(content="<html><body><h1>Turjuman Frontend</h1><p>Error: index.html not found.</p></body></html>", status_code=404)

# --- Add Langserve Routes ---
# This exposes the standard LangGraph endpoints under the specified path prefix.
add_routes(
    app,
    langgraph_app, # The compiled LangGraph application instance
    path="/translate_graph", # The base path for the LangGraph API endpoints
    input_type=TranslationState, # Define the expected input schema (for /invoke, /batch etc.)
    output_type=TranslationState, # Define the expected output schema (for /invoke, /batch etc.)
    # Expose 'thread_id' for configuring checkpointing and resuming runs
    # Expose 'recursion_limit' for safety
    config_keys=["configurable", "thread_id", "recursion_limit"],
    enable_feedback_endpoint=True, # Enables the /feedback endpoint (optional)
    enable_public_trace_link_endpoint=True, # Enables /public_trace_link (optional)
    playground_type="default", # Use default playground since we're not using chat messages
)

# --- Optional: Simple HTML Frontend Route ---
# This is very basic, a real frontend would be separate (e.g., React/Vue/Svelte)
# Mount a static directory if you have CSS/JS files
# Example: os.makedirs("static", exist_ok=True); app.mount("/static", StaticFiles(directory="static"), name="static")
# Setup Jinja2 templates if needed
# Example: templates = Jinja2Templates(directory="templates")
# @app.get("/", response_class=HTMLResponse, tags=["Frontend"])
# async def read_root(request: Request):
#     # Basic HTML form to kick off a job (replace with real frontend logic)
#     return templates.TemplateResponse("index.html", {"request": request})

# --- Job Management Routes ---
@app.post("/jobs", tags=["Jobs"])
async def create_job(request: Request):
    """Create a new translation job."""
    data = await request.json()
    job_id = await job_queue.enqueue_job(data)
    return {"job_id": job_id, "status": "pending"}

@app.get("/jobs", tags=["Jobs"])
async def list_jobs(limit: int = 100, offset: int = 0):
    """List all translation jobs."""
    jobs = await job_queue.list_jobs(limit, offset)
    return {"jobs": jobs}

@app.get("/jobs/{job_id}", tags=["Jobs"])
async def get_job(job_id: str):
    """Get details for a specific job."""
    job_details = await job_queue.get_job_details(job_id)
    if "error" in job_details:
        return JSONResponse(status_code=404, content=job_details)
    return job_details

@app.get("/jobs/{job_id}/download", tags=["Jobs"])
async def download_job(job_id: str):
    """Download the final translation for a job."""
    from .database import get_job
    job = await get_job(job_id)
    
    if not job or not job.get("final_document"):
        return JSONResponse(
            status_code=404,
            content={"error": "Job not found or translation not completed"}
        )
    
    final_document = job.get("final_document")
    source_lang = job.get("source_lang")
    target_lang = job.get("target_lang")
    
    # Use the stored filename if available, otherwise create a default one
    if job.get("filename"):
        filename = f"{job['filename']}.txt"
    else:
        filename = f"translation_{source_lang}_to_{target_lang}_{job_id}.txt"
    
    # Return as downloadable file
    return Response(
        content=final_document,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job_endpoint(job_id: str):
    """Delete a job and all related data."""
    from .database import delete_job, get_job
    
    # Check if job exists
    job = await get_job(job_id)
    if not job:
        return JSONResponse(
            status_code=404,
            content={"detail": f"Job {job_id} not found"}
        )
    
    # Delete the job
    success = await delete_job(job_id)
    if success:
        return JSONResponse(
            status_code=200,
            content={"detail": f"Job {job_id} deleted successfully"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to delete job {job_id}"}
        )

@app.get("/jobs/{job_id}/stream", tags=["Jobs"])
async def stream_job_updates(job_id: str):
    """Stream updates for a specific job."""
    async def event_generator():
        from .database import get_job, get_logs, get_chunks, get_glossary, get_critiques, get_metrics
        
        last_update_time = 0
        
        while True:
            job = await get_job(job_id)
            
            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            
            job_dict = dict(job)
            
            # Get current time
            current_time = time.time()
            
            # Always send updates at least every second
            if current_time - last_update_time >= 1:
                last_update_time = current_time
                
                # Get recent logs
                logs = await get_logs(job_id, limit=20)
                job_dict["recent_logs"] = logs
                
                # Get chunks if available
                chunks = await get_chunks(job_id)
                if chunks:
                    job_dict["chunks"] = chunks
                
                # Get glossary if available
                glossary = await get_glossary(job_id)
                if glossary:
                    job_dict["glossary"] = glossary
                
                # Get critiques if available
                critiques = await get_critiques(job_id)
                if critiques:
                    job_dict["critiques"] = critiques
                
                # Get metrics if available
                metrics = await get_metrics(job_id)
                if metrics:
                    job_dict["metrics"] = metrics
                
                yield f"data: {json.dumps(job_dict, default=str)}\n\n"
            
            # If job is completed or failed, end the stream
            if job_dict.get("status") in ["completed", "failed"]:
                break
            
            # Wait before checking again
            await asyncio.sleep(1)
        
        # Send end event
        yield "event: end\ndata: {}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
#     return {"message": "Job listing endpoint not fully implemented."}

@app.get("/health", tags=["Health"])
async def health():
    """Basic health check endpoint."""
    return {"status": "ok"}

@app.get("/providers", tags=["Providers"])
async def get_providers():
    return list_available_providers()

# --- SSE Streaming Endpoint for Translation Progress ---
@app.get("/translate_graph/stream")
async def stream_translation(
    input: str = Query(..., description="JSON-encoded input object"),
    config: str = Query(..., description="JSON-encoded config object")
):
    """
    Streams translation progress/results as Server-Sent Events (SSE).
    """
    try:
        input_obj = json.loads(input)
        config_obj = json.loads(config)
    except Exception as e:
        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'error': 'Invalid input/config JSON', 'details': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    async def translation_stream():
        import uuid
        run_id = str(uuid.uuid4())
        feedback_tokens = []
        state_queue = queue.Queue()
        log_queue = queue.Queue()

        # Custom logging handler to stream logs to the frontend
        class SSELogHandler(logging.Handler):
            def emit(self, record):
                try:
                    log_entry = self.format(record)
                    log_queue.put(log_entry)
                except Exception:
                    pass

        sse_log_handler = SSELogHandler()
        sse_log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s'))
        # Attach to root logger to capture all logs, including from worker threads
        logging.getLogger().addHandler(sse_log_handler)
        # Optionally, ensure all loggers propagate to root
        logging.getLogger("turjuman").propagate = True

        class ProgressHandler(BaseCallbackHandler):
            def on_chain_end(self, outputs, **kwargs):
                # outputs is the current state after node execution
                state_queue.put(copy.deepcopy(outputs))

        result_holder = {}

        def run_workflow():
            try:
                # Pass the callback handler to the graph/app
                final_state = graph.app.invoke(
                    input_obj,
                    config={"callbacks": [ProgressHandler()]}
                )
                # Always put the final state in the queue, even if callback missed it
                import logging
                logger = logging.getLogger("turjuman")
                # logger.info(f"Workflow returned final_state: {type(final_state)}")

                if final_state is None:
                    logger.error("Workflow invocation returned None!")
                    raise ValueError("Workflow returned None, cannot process final state.")

                # Ensure final_document and job_id are present
                # Safely convert final_state to dict if possible
                if hasattr(final_state, "items"):
                    final_state_dict = dict(final_state)
                elif isinstance(final_state, dict):
                     final_state_dict = final_state
                else:
                    # If it's not dict-like, create a basic dict with an error or minimal info
                    logger.warning(f"Final state is not dict-like: {type(final_state)}. Creating basic dict.")
                    final_state_dict = {"error": "Workflow returned unexpected final state type."}
                    # Try to add job_id if possible
                    if hasattr(final_state, "job_id"):
                         final_state_dict["job_id"] = getattr(final_state, "job_id", None)

                # Ensure final_document is present
                if not final_state_dict.get("final_document"):
                    if final_state_dict.get("final_chunks"):
                        final_state_dict["final_document"] = "\n".join(final_state_dict["final_chunks"])
                    elif final_state_dict.get("parallel_worker_results"):
                        final_state_dict["final_document"] = "\n".join(
                            r.get("refined_text") or r.get("initial_translation") or ""
                            for r in final_state_dict.get("parallel_worker_results", []) # Add default empty list
                        )
                    else:
                        final_state_dict["final_document"] = None

                # Ensure job_id is present
                if "job_id" not in final_state_dict and hasattr(final_state, "job_id"):
                     final_state_dict["job_id"] = getattr(final_state, "job_id", None)
                elif "job_id" not in final_state_dict and "config" in input_obj: # Fallback to input job_id
                     final_state_dict["job_id"] = input_obj.get("job_id")


                # logger.info(f"Final state to SSE: {final_state_dict}")
                state_queue.put(copy.deepcopy(final_state_dict))
                result_holder["final"] = final_state_dict
            except Exception as e:
                # Use logging.getLogger directly to avoid scope issues
                logging.getLogger("turjuman").exception("Error during workflow execution or final state processing:")
                result_holder["error"] = str(e)
                state_queue.put({"error": str(e)})

        t = threading.Thread(target=run_workflow)
        t.start()

        while t.is_alive() or not log_queue.empty() or not state_queue.empty():
            queues_were_empty = True
            # Drain logs
            while not log_queue.empty():
                try:
                    log_item = log_queue.get_nowait()
                    yield f"event: log\ndata: {json.dumps({'log': log_item})}\n\n"
                    queues_were_empty = False
                except queue.Empty:
                    break # Should not happen with check, but safety
                except Exception as e:
                    yield f"event: error\ndata: {json.dumps({'error': f'Log processing error: {e}'})}\n\n"

            # Drain state updates
            while not state_queue.empty():
                try:
                    item = state_queue.get_nowait()
                    wrapped = {
                        "output": item,
                        "metadata": {
                            "run_id": run_id,
                            "feedback_tokens": feedback_tokens
                        }
                    }
                    yield f"data: {json.dumps(wrapped, default=str)}\n\n"
                    queues_were_empty = False
                except queue.Empty:
                    break # Should not happen with check, but safety
                except Exception as e:
                    yield f"event: error\ndata: {json.dumps({'error': f'State processing error: {e}'})}\n\n"

            # If thread is alive and queues were empty, pause briefly
            if t.is_alive() and queues_were_empty:
                await asyncio.sleep(0.1)

        # After loop: thread is dead and queues are empty
        # Send final error if it occurred and wasn't sent via state_queue
        if "error" in result_holder:
             # Check if the error was already sent (e.g., via state_queue.put({"error": ...}))
             # This check is tricky; assume it might not have been sent if loop exited due to thread death
             # A more robust way might involve a flag or checking the last sent message type
             yield f"data: {json.dumps({'error': result_holder['error']}, default=str)}\n\n"

        # Send the final end event
        yield "event: end\ndata: {}\n\n"

        # Remove the custom log handler after streaming
        logging.getLogger("turjuman").removeHandler(sse_log_handler)

    return StreamingResponse(translation_stream(), media_type="text/event-stream")
    """
    Returns a list of enabled LLM providers and their models.
    """
    return list_available_providers()

# --- Environment Variables Management Routes ---
@app.get("/env-variables", tags=["Configuration"])
async def get_env_variables():
    """Get all environment variables."""
    from .database import get_env_variables
    env_vars = await get_env_variables()
    return {"env_variables": env_vars}

@app.post("/env-variables", tags=["Configuration"])
async def create_env_variable(request: Request):
    """Create or update an environment variable."""
    from .database import set_env_variable, save_env_variables_to_file
    data = await request.json()
    
    key = data.get("key")
    value = data.get("value")
    description = data.get("description")
    
    if not key or not value:
        return JSONResponse(
            status_code=400,
            content={"detail": "Key and value are required"}
        )
    
    success = await set_env_variable(key, value, description)
    if success:
        # Also save to .env file
        file_success = await save_env_variables_to_file()
        if file_success:
            # Update os.environ with the new value
            os.environ[key] = value
            return {"detail": f"Environment variable {key} set successfully and saved to .env file"}
        else:
            return {"detail": f"Environment variable {key} set in database but failed to update .env file"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to set environment variable {key}"}
        )

@app.delete("/env-variables/{key}", tags=["Configuration"])
async def delete_env_variable_endpoint(key: str):
    """Delete an environment variable."""
    from .database import delete_env_variable, save_env_variables_to_file
    success = await delete_env_variable(key)
    if success:
        # Also update .env file
        file_success = await save_env_variables_to_file()
        if file_success:
            # Remove from os.environ if present
            if key in os.environ:
                del os.environ[key]
            return {"detail": f"Environment variable {key} deleted successfully and removed from .env file"}
        else:
            return {"detail": f"Environment variable {key} deleted from database but failed to update .env file"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to delete environment variable {key}"}
        )

# --- LLM Configuration Routes ---
@app.get("/llm-configs", tags=["Configuration"])
async def get_llm_configs():
    """Get all LLM configurations."""
    from .database import get_llm_configs
    configs = await get_llm_configs()
    return {"llm_configs": configs}

@app.get("/llm-configs/default", tags=["Configuration"])
async def get_default_llm_config():
    """Get the default LLM configuration."""
    from .database import get_default_llm_config
    config = await get_default_llm_config()
    if config:
        return config
    else:
        return JSONResponse(
            status_code=404,
            content={"detail": "No default LLM configuration found"}
        )

@app.post("/llm-configs", tags=["Configuration"])
async def create_llm_config(request: Request):
    """Create a new LLM configuration."""
    from .database import save_llm_config
    data = await request.json()
    
    set_as_default = data.pop("set_as_default", False)
    
    if not data.get("provider") or not data.get("model"):
        return JSONResponse(
            status_code=400,
            content={"detail": "Provider and model are required"}
        )
    
    config_id = await save_llm_config(data, set_as_default)
    return {"id": config_id, "detail": "LLM configuration saved successfully"}

@app.put("/llm-configs/{config_id}", tags=["Configuration"])
async def update_llm_config_endpoint(config_id: int, request: Request):
    """Update an existing LLM configuration."""
    from .database import update_llm_config
    data = await request.json()
    
    set_as_default = data.pop("set_as_default", False)
    
    success = await update_llm_config(config_id, data, set_as_default)
    if success:
        return {"detail": f"LLM configuration {config_id} updated successfully"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to update LLM configuration {config_id}"}
        )

@app.delete("/llm-configs/{config_id}", tags=["Configuration"])
async def delete_llm_config_endpoint(config_id: int):
    """Delete an LLM configuration."""
    from .database import delete_llm_config
    success = await delete_llm_config(config_id)
    if success:
        return {"detail": f"LLM configuration {config_id} deleted successfully"}
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to delete LLM configuration {config_id}"}
        )

# --- Run with Uvicorn (if running this file directly) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8051)) # Allow port override via environment variable
    host = os.getenv("HOST", "127.0.0.1") # Default to localhost for direct run security
    reload_dev = os.getenv("DEV_RELOAD", "false").lower() == "true" # Enable reload via env var

    print(f"Starting Uvicorn server on {host}:{port} (Reload: {reload_dev})")
    # Use reload=True only for development
    uvicorn.run(
        "server:app", # Point to the FastAPI app instance in this file
        host=host,
        port=port,
        reload=reload_dev, # Enable reload only if DEV_RELOAD=true
        reload_dirs=["src"] if reload_dev else None # Watch src directory for changes if reloading
        )

# To run using the Langserve/LangGraph CLI (often simpler):
# Ensure you are in the project root directory
# Activate your conda environment: conda activate langgraph_translator
# Run: langgraph server -m src.server:app --host 0.0.0.0 --port 8051
# The CLI handles finding the 'app' instance (which points to the compiled graph via add_routes).
