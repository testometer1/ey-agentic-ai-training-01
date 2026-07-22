"""
Loan Underwriting Desk — the web backend.
-----------------------------------------
Three routes:
  POST /api/stream  — run an application; STREAM live events as the agents work
  POST /api/resume  — the human's Approve / Decline for a borderline (paused) case
  GET  /            — serve the React page (frontend/index.html)

Run (from this folder):  python server.py   →  open http://127.0.0.1:8500
"""
import uuid                                              # to make a unique id for each run
from pathlib import Path                                 # a tidy way to build file paths
from typing import cast                                  # tells the type checker "trust me, it's this type"
from fastapi import FastAPI                              # the web framework
from fastapi.responses import HTMLResponse, StreamingResponse   # reply types: a web page, and a live stream
from fastapi.middleware.cors import CORSMiddleware       # lets the browser page talk to this server
from pydantic import BaseModel                           # describes the shape of incoming JSON
from langchain_core.runnables import RunnableConfig      # the config type LangGraph expects
from langgraph.types import Command                      # used to resume a paused run
from graph import build_graph                            # builds our multi-agent graph
from state import LoanState                              # the shape of the application data
from events import to_ui_event, ndjson                   # our event translator + line formatter

PORT = 8500                                    # NOT 8000 — Docker Desktop often holds 8000
app = FastAPI(title="Loan Underwriting Desk")  # create the web app
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])   # let the browser call us
GRAPH = build_graph()                          # the multi-agent brain, built once


class Application(BaseModel):                   # what the form sends us
    name: str                                            # applicant's name
    income: float                                        # monthly income
    cibil: int                                           # credit score
    amount: float                                        # loan amount requested
    tenure: int                                          # loan length in years
    purpose: str                                         # what the loan is for


class Resume(BaseModel):                        # what the Approve / Decline buttons send
    thread_id: str                                       # which paused run to continue
    verdict: str                                         # the human's choice: approve / decline


def new_thread() -> tuple[str, RunnableConfig]:          # make a fresh id + config for one run
    """A fresh id for one application run, plus the config LangGraph wants."""
    thread_id = uuid.uuid4().hex                         # a random unique id
    return thread_id, {"configurable": {"thread_id": thread_id}}   # the id + the config LangGraph needs


@app.post("/api/stream")                                 # route: start an application run
async def stream(application: Application):              # runs the agents and streams the events
    """Run the agents and stream what happens, one event at a time."""

    async def events():                        # this inner generator produces the stream
        thread_id, thread = new_thread()                 # a fresh run id + config
        payload = cast(LoanState, application.model_dump())   # the form data as our LoanState
        current_agent = None                             # who is working right now (none yet)

        async for raw in GRAPH.astream_events(payload, thread, version="v2"):   # walk the live event stream
            event = to_ui_event(raw, current_agent)     # translate it (or None)
            if event is None:                            # not one we care about?
                continue                                 # skip it
            if event["t"] == "agent_start":              # an agent just started?
                current_agent = event["id"]             # remember who is working now
            yield ndjson(event)                          # send the event to the browser

        # the agents are done — either a decision, or paused for a human
        final = GRAPH.get_state(thread).values           # read the final state
        if final.get("decision"):                        # did we reach a decision?
            yield ndjson({"t": "decision", "decision": final["decision"]})   # send it
        else:                                            # otherwise it paused for a human
            yield ndjson({"t": "referred", "thread_id": thread_id,   # tell the UI to show Approve/Decline
                          "recommendation": final.get("recommendation"),
                          "rationale": final.get("rationale")})
        yield ndjson({"t": "done"})                      # signal the stream is finished

    return StreamingResponse(events(), media_type="application/x-ndjson")   # stream those lines to the browser


@app.post("/api/resume")                                 # route: the human's Approve / Decline
def resume(r: Resume) -> dict:                           # continue a paused run with the human's choice
    """The human clicked Approve / Decline — resume the paused run, return the outcome."""
    thread: RunnableConfig = {"configurable": {"thread_id": r.thread_id}}   # point back to the paused run
    state = GRAPH.invoke(Command(resume=r.verdict), thread)   # resume it with the human's verdict
    return {"decision": state.get("decision")}           # send back the final decision


@app.get("/", response_class=HTMLResponse)               # route: the home page
def index() -> str:                                      # serve the React UI
    """Serve the React page from ../frontend/index.html."""
    return (Path(__file__).parent.parent / "frontend" / "index.html").read_text()   # read + return the HTML file


if __name__ == "__main__":                               # only when run directly (python server.py)
    import uvicorn                                        # the web server that runs our app
    print(f"\n  ▶  Open  http://127.0.0.1:{PORT}  in your browser\n")   # a friendly hint in the terminal
    uvicorn.run(app, host="127.0.0.1", port=PORT)        # start serving on port 8500
