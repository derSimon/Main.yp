from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()

jobs = {}

class JobCreate(BaseModel):
    youtube_url: str
    language: str = "de"
    target_duration: int = 30

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/jobs")
def create_job(job: JobCreate):
    job_id = str(uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "youtube_url": job.youtube_url,
        "language": job.language,
        "target_duration": job.target_duration
    }
    return jobs[job_id]

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]
