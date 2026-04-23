from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import uuid
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

class VideoRequest(BaseModel):
    url: str

def is_valid_youtube_url(url: str) -> bool:
    pattern = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+"
    return bool(re.match(pattern, url))

async def process_video(job_id: str, url: str):
    """Simuliert den Workflow – hier später echte Verarbeitung"""
    jobs[job_id]["status"] = "downloading"
    jobs[job_id]["message"] = "⬇️ Video wird heruntergeladen..."
    await asyncio.sleep(2)

    jobs[job_id]["status"] = "transcribing"
    jobs[job_id]["message"] = "🎙️ Audio wird transkribiert..."
    await asyncio.sleep(2)

    jobs[job_id]["status"] = "analyzing"
    jobs[job_id]["message"] = "🤖 KI analysiert beste Momente..."
    await asyncio.sleep(2)

    jobs[job_id]["status"] = "cutting"
    jobs[job_id]["message"] = "✂️ Clips werden geschnitten..."
    await asyncio.sleep(2)

    jobs[job_id]["status"] = "done"
    jobs[job_id]["message"] = "✅ Workflow abgeschlossen! Clips sind bereit."

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/process")
async def start_process(request: VideoRequest, background_tasks: BackgroundTasks):
    if not is_valid_youtube_url(request.url):
        return JSONResponse(status_code=400, content={"error": "Ungültige YouTube-URL"})

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"status": "started", "message": "🚀 Workflow gestartet!", "url": request.url}
    background_tasks.add_task(process_video, job_id, request.url)

    return {"job_id": job_id, "message": "Workflow wurde gestartet!"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return JSONResponse(status_code=404, content={"error": "Job nicht gefunden"})
    return jobs[job_id]
