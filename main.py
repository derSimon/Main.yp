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

jobs = {}

class VideoRequest(BaseModel):
    url: str

def is_valid_youtube_url(url: str) -> bool:
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)(/|$)"
    return bool(re.match(pattern, url))

async def process_video(job_id: str, url: str):
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

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shorts Generator</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  :root{--bg:#0a0a0a;--surface:#111;--border:#1e1e1e;--accent:#ff3d3d;--accent2:#ff8c42;--text:#f0ede8;--muted:#666;--success:#3dff8f}
  body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
  .container{position:relative;z-index:1;width:100%;max-width:560px}
  .logo{font-family:'Syne',sans-serif;font-weight:800;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:48px}
  h1{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(36px,8vw,56px);line-height:1.0;margin-bottom:12px;letter-spacing:-.02em}
  h1 span{display:block;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
  .subtitle{color:var(--muted);font-size:15px;font-weight:300;margin-bottom:40px;line-height:1.6}
  .input-group{display:flex;flex-direction:column;gap:12px;margin-bottom:24px}
  .input-wrapper{position:relative;display:flex;align-items:center}
  .yt-icon{position:absolute;left:16px;width:20px;height:20px;opacity:.5;color:var(--text)}
  input[type=text]{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px 20px 18px 48px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:15px;outline:none;transition:border-color .2s,box-shadow .2s}
  input[type=text]::placeholder{color:var(--muted)}
  input[type=text]:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(255,61,61,.1)}
  button{width:100%;padding:18px;background:var(--accent);color:#fff;border:none;border-radius:12px;font-family:'Syne',sans-serif;font-weight:700;font-size:15px;letter-spacing:.05em;text-transform:uppercase;cursor:pointer;transition:transform .15s,box-shadow .15s}
  button:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 8px 32px rgba(255,61,61,.35)}
  button:disabled{opacity:.5;cursor:not-allowed}
  .status-card{margin-top:24px;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px;display:none;animation:slideUp .3s ease}
  .status-card.visible{display:block}
  @keyframes slideUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
  .status-label{font-size:11px;font-weight:500;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);margin-bottom:10px}
  .status-message{font-family:'Syne',sans-serif;font-size:18px;font-weight:700;margin-bottom:20px;min-height:28px}
  .progress-track{height:3px;background:var(--border);border-radius:99px;overflow:hidden;margin-bottom:16px}
  .progress-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px;width:0%;transition:width .6s ease}
  .steps{display:flex;flex-direction:column;gap:8px}
  .step{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--muted);transition:color .3s}
  .step.active{color:var(--text)}.step.done{color:var(--success)}
  .step-dot{width:6px;height:6px;border-radius:50%;background:var(--border);flex-shrink:0;transition:background .3s}
  .step.active .step-dot{background:var(--accent);box-shadow:0 0 8px var(--accent)}
  .step.done .step-dot{background:var(--success)}
  .done-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(61,255,143,.1);border:1px solid rgba(61,255,143,.3);color:var(--success);border-radius:99px;padding:6px 14px;font-size:13px;font-weight:500;margin-top:12px}
  .error-msg{color:var(--accent);font-size:13px;margin-top:8px;display:none}
  .footer{margin-top:40px;font-size:12px;color:#333;text-align:center}
</style>
</head>
<body>
<div class="container">
  <div class="logo">◆ Shorts Generator</div>
  <h1>Dreh jedes <span>Video in Shorts.</span></h1>
  <p class="subtitle">YouTube-Link einfügen – KI findet die besten Momente, schneidet sie und postet automatisch.</p>
  <div class="input-group">
    <div class="input-wrapper">
      <svg class="yt-icon" viewBox="0 0 24 24" fill="none"><path d="M22.54 6.42C22.42 5.95 22.18 5.51 21.84 5.16C21.5 4.81 21.07 4.55 20.6 4.42C18.88 4 12 4 12 4C12 4 5.12 4 3.4 4.46C2.93 4.59 2.5 4.85 2.16 5.2C1.82 5.55 1.58 5.99 1.46 6.46C1.15 8.21 0.99 9.98 1 11.75C0.99 13.54 1.14 15.32 1.46 17.08C1.59 17.54 1.84 17.96 2.18 18.29C2.52 18.63 2.94 18.87 3.4 19C5.12 19.46 12 19.46 12 19.46C12 19.46 18.88 19.46 20.6 19C21.07 18.87 21.5 18.61 21.84 18.26C22.18 17.91 22.42 17.47 22.54 17C22.85 15.27 23.01 13.51 23 11.75C23.01 9.96 22.85 8.18 22.54 6.42Z" fill="currentColor"/><path d="M9.75 15.02L15.5 11.75L9.75 8.48V15.02Z" fill="#0a0a0a"/></svg>
      <input type="text" id="urlInput" placeholder="https://youtube.com/watch?v=..." />
    </div>
    <button id="startBtn" onclick="startWorkflow()">Workflow starten →</button>
    <p class="error-msg" id="errorMsg">⚠️ Bitte eine gültige YouTube-URL eingeben.</p>
  </div>
  <div class="status-card" id="statusCard">
    <div class="status-label">Status</div>
    <div class="status-message" id="statusMessage">🚀 Workflow gestartet!</div>
    <div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
    <div class="steps">
      <div class="step" id="step-started"><span class="step-dot"></span>Workflow gestartet</div>
      <div class="step" id="step-downloading"><span class="step-dot"></span>Video herunterladen</div>
      <div class="step" id="step-transcribing"><span class="step-dot"></span>Audio transkribieren</div>
      <div class="step" id="step-analyzing"><span class="step-dot"></span>KI analysiert Momente</div>
      <div class="step" id="step-cutting"><span class="step-dot"></span>Clips schneiden</div>
      <div class="step" id="step-done"><span class="step-dot"></span>Fertig!</div>
    </div>
    <div id="doneBadge" style="display:none"><div class="done-badge">✓ Clips bereit zum Posten</div></div>
  </div>
  <div class="footer">Powered by FastAPI · Railway · OpenAI</div>
</div>
<script>
  const STEPS=['started','downloading','transcribing','analyzing','cutting','done'];
  const PROGRESS={started:5,downloading:25,transcribing:50,analyzing:70,cutting:88,done:100};
  let pollInterval=null;
  async function startWorkflow(){
    const url=document.getElementById('urlInput').value.trim();
    const errorMsg=document.getElementById('errorMsg');
    const btn=document.getElementById('startBtn');
    errorMsg.style.display='none';
    if(!url||(!url.includes('youtube')&&!url.includes('youtu.be'))){errorMsg.style.display='block';return;}
    btn.disabled=true;btn.textContent='Startet...';
    try{
      const res=await fetch('/process',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
      if(!res.ok){const err=await res.json();errorMsg.textContent='⚠️ '+(err.error||'Fehler.');errorMsg.style.display='block';btn.disabled=false;btn.textContent='Workflow starten →';return;}
      const data=await res.json();
      document.getElementById('statusCard').classList.add('visible');
      pollStatus(data.job_id);
    }catch(e){errorMsg.textContent='⚠️ Server nicht erreichbar.';errorMsg.style.display='block';btn.disabled=false;btn.textContent='Workflow starten →';}
  }
  function updateUI(status){
    document.getElementById('statusMessage').textContent=status.message;
    document.getElementById('progressFill').style.width=(PROGRESS[status.status]||5)+'%';
    STEPS.forEach(s=>{
      const el=document.getElementById('step-'+s);if(!el)return;
      el.className='step';
      const idx=STEPS.indexOf(s),curIdx=STEPS.indexOf(status.status);
      if(idx<curIdx)el.classList.add('done');else if(idx===curIdx)el.classList.add('active');
    });
    if(status.status==='done'){document.getElementById('doneBadge').style.display='block';clearInterval(pollInterval);document.getElementById('startBtn').disabled=false;document.getElementById('startBtn').textContent='Weiteres Video →';}
  }
  function pollStatus(jobId){pollInterval=setInterval(async()=>{try{const res=await fetch('/status/'+jobId);const data=await res.json();updateUI(data);}catch(e){}},1500);}
  document.addEventListener('DOMContentLoaded',()=>{document.getElementById('urlInput').addEventListener('keydown',e=>{if(e.key==='Enter')startWorkflow();});});
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML

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
