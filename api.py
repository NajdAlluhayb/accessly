"""FastAPI adapter; optional isolated public-demo mode. Agent logic remains in main.py."""
import json
import logging
import os
import runpy
import threading
import sys

# Agent streaming output includes Unicode; Windows redirected consoles may use cp1252.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
from result_presenter import format_result, unavailable
import contextvars
from deployment_runtime import PUBLIC, OWNER, ORIGINS, visitor_directory, visitor_from_header, reserve_action, require_public_url, configure_agent, authorize_approval
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)  # Existing tools use relative profile/request paths.
app = FastAPI(title="Accessly API")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type", "Authorization"])
lock = threading.RLock()
worker = ThreadPoolExecutor(max_workers=1)
sessions = {}
jobs = {}
session_context = {}

@app.middleware("http")
async def visitor_session(request: Request, call_next):
    protected = request.url.path.startswith(("/api/", "/requests/", "/jobs/")) or request.url.path in ("/profile", "/chat", "/requests")
    if not PUBLIC or not protected or request.method == "OPTIONS" or request.url.path in ("/api/health", "/health"):
        return await call_next(request)
    try:
        owner = visitor_from_header(request.headers.get("Authorization"))
    except HTTPException as error:
        return JSONResponse({"detail": error.detail}, status_code=error.status_code)
    token = OWNER.set(owner)
    try:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response
    finally:
        OWNER.reset(token)

def owned_session(session_id):
    if session_id not in sessions or (PUBLIC and session_context.get(session_id, {}).get("owner") != OWNER.get()):
        raise HTTPException(404, "Conversation expired or unavailable. Analyze the event again.")

def owned_job(job_id):
    if job_id not in jobs:
        raise HTTPException(404, "Action not found")
    owned_session(jobs[job_id]["session_id"])
    return jobs[job_id]

def visitor_busy():
    return any(j["status"] == "processing" and (not PUBLIC or session_context.get(j["session_id"], {}).get("owner") == OWNER.get()) for j in jobs.values())

class Profile(BaseModel):
    needs: list[str] = Field(min_length=1, max_length=30)

class Event(BaseModel):
    url: HttpUrl

class Message(BaseModel):
    message: str = Field(min_length=1, max_length=12000)


def read_json(name, fallback):
    path = visitor_directory() / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/profile")
@app.get("/api/profile")
def profile():
    with lock:
        return read_json("user_profile.json", {"needs": []})

@app.post("/profile")
@app.post("/api/profile")
@app.put("/api/profile")
def save_profile(body: Profile):
    with lock:
        if visitor_busy():
            raise HTTPException(409, "Wait for the active agent action before changing preferences.")
        current = read_json("user_profile.json", {})
        current["needs"] = list(dict.fromkeys(n.strip() for n in body.needs if n.strip()))
        if not current["needs"]:
            raise HTTPException(422, "Select at least one accessibility need.")
        path = visitor_directory() / "user_profile.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
        temp.replace(path)
        return current

@app.get("/requests")
@app.get("/api/requests")
def requests():
    with lock:
        return read_json("requests.json", [])


def submit(session_id, message):
    with lock:
        if visitor_busy():
            raise HTTPException(409, "An agent action is already running. Please wait.")
        if PUBLIC and sum(j["status"] == "processing" for j in jobs.values()) >= 8:
            raise HTTPException(429, "The demo queue is full. Please try again shortly.")
        reserve_action()
        job_id = str(uuid4())
        jobs[job_id] = {"id": job_id, "session_id": session_id, "status": "processing", "response": ""}
    context = session_context.setdefault(session_id, {"url": None, "needs": read_json("user_profile.json", {}).get("needs", []), "result": None, "owner": OWNER.get(), "reference": session_id[:12]})
    def execute():
        try:
            if sessions[session_id] is None:
                namespace = runpy.run_path(str(ROOT / "main.py"))
                sessions[session_id] = namespace["agent"]
                configure_agent(namespace, context)
            authorize_approval(message, context)
            if PUBLIC:
                result = sessions[session_id](message, limits={"turns": 20, "total_tokens": 160000})
            else:
                result = sessions[session_id](message)
            with lock:
                jobs[job_id]["response"] = str(result)
            present_job(job_id)
        except Exception:
            logging.exception("Agent action failed")
            with lock:
                jobs[job_id].update(status="failed", response="The agent action failed. Check the backend terminal for details. No automatic retry was made.")
        finally:
            if PUBLIC and context.get("browser"):
                try:
                    context["browser"]._cleanup()
                except Exception:
                    logging.exception("Browser cleanup failed")
    worker.submit(contextvars.copy_context().run, execute)
    return dict(jobs[job_id])

def present_job(job_id):
    job = jobs[job_id]
    context = session_context[job["session_id"]]
    try:
        result = format_result(job["response"], context["needs"], context["url"], sessions[job["session_id"]].model, context["result"])
        result["requests"] = [r for r in read_json("requests.json", []) if r.get("event_url", "").rstrip("/") == (context["url"] or "").rstrip("/")]
        context["result"] = result
    except Exception:
        logging.exception("Presentation failed for job %s; agent action will not be repeated", job_id)
        result = unavailable()
    with lock:
        job.update(status="completed", result=result)

@app.post("/api/jobs/{job_id}/presentation", status_code=202)
def retry_presentation(job_id: str):
    with lock:
        job = owned_job(job_id)
        if not job or not job.get("response") or job["status"] == "failed":
            raise HTTPException(404, "No completed agent response to format.")
        if visitor_busy():
            raise HTTPException(409, "An action is still running. Please wait.")
        reserve_action()
        job["status"] = "processing"
        worker.submit(contextvars.copy_context().run, present_job, job_id)
        return dict(job)

@app.post("/api/events", status_code=202)
def analyze(body: Event):
    if PUBLIC:
        try:
            require_public_url(str(body.url))
        except (ValueError, OSError):
            raise HTTPException(422, "Use a publicly accessible HTTP(S) event URL.")
    session_id = str(uuid4())
    with lock:
        if len(sessions) >= 100:
            raise HTTPException(409, "Restart the local backend to clear old conversations.")
        sessions[session_id] = None
        session_context[session_id] = {"url": str(body.url), "needs": read_json("user_profile.json", {}).get("needs", []), "result": None, "owner": OWNER.get(), "reference": session_id[:12]}
    prompt = "Check this event: " + str(body.url)
    if PUBLIC:
        prompt += "\nPublic demonstration: browse in read-only mode using navigate and get_text. Never submit a form. Include [Accessly " + session_id[:12] + "] in every email draft subject. Email is test-inbox only; wait for exact approval."
    return submit(session_id, prompt)

@app.post("/api/sessions/{session_id}/messages", status_code=202)
def message(session_id: str, body: Message):
    owned_session(session_id)
    return submit(session_id, body.message)

@app.post("/requests/{request_id}/check", status_code=202)
@app.post("/api/requests/{request_id}/check", status_code=202)
def check_reply(request_id: str):
    if not any(r["request_id"] == request_id for r in requests()):
        raise HTTPException(404, "Request not found")
    session_id = str(uuid4())
    sessions[session_id] = None
    record = next(r for r in requests() if r["request_id"] == request_id)
    session_context[session_id] = {"url": record.get("event_url"), "needs": list(record.get("accommodations", {})), "result": None, "owner": OWNER.get(), "reference": session_id[:12]}
    return submit(session_id, "Check reply for " + request_id)

@app.get("/jobs/{job_id}")
@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    with lock:
        return dict(owned_job(job_id))

class Chat(BaseModel):
    url: HttpUrl | None = None
    session_id: str | None = None
    message: str | None = Field(default=None, min_length=1, max_length=12000)

@app.post("/chat", status_code=202)
@app.post("/api/chat", status_code=202)
def chat(body: Chat):
    if body.session_id and body.message and body.url is None:
        return message(body.session_id, Message(message=body.message))
    if body.url is not None and body.session_id is None and body.message is None:
        return analyze(Event(url=body.url))
    raise HTTPException(422, "Provide url for a new event, or session_id and message for a follow-up.")

# Production UI is mounted after API routes.
if (ROOT / "frontend" / "dist").is_dir():
    app.mount("/", StaticFiles(directory=ROOT / "frontend" / "dist", html=True), name="frontend")
