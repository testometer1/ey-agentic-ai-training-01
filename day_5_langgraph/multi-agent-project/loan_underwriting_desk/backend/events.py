"""
Turn raw LangGraph events into the simple events our UI understands.
-------------------------------------------------------------------
While the agents work, GRAPH.astream_events(...) fires MANY low-level events. This
file keeps only the few we care about and translates each into a tidy little dict
the browser can read — so server.py can stay short and about the web routes.
"""
import json                                            # to turn Python dicts into text lines

# which graph node is which agent:  node name -> (id, display name)
AGENTS = {                                             # lookup: graph node name → (id, display name)
    "credit_node": ("credit", "Credit Analyst"),
    "policy_node": ("policy", "Policy Officer"),
    "fraud_node":  ("fraud",  "Fraud Investigator"),
}


def ndjson(event) -> str:                              # turn one event into a single text line
    """Format one event as a single line of JSON — the streaming format."""
    return json.dumps(event) + "\n"                    # one JSON object per line


def _tool_output(data) -> str:                         # pull a short, tidy string out of a tool result
    """The text a tool returned, trimmed so the UI stays tidy."""
    result = data.get("output")                        # the raw tool result
    text = getattr(result, "content", None) or str(result)   # its text, however it is shaped
    return text[:140]                                  # keep it short for the UI


def to_ui_event(raw, current_agent):                   # translate one raw event → one UI event (or None)
    """Translate ONE LangGraph event into ONE UI event — or None to ignore it."""
    kind = raw["event"]                        # e.g. 'on_tool_start'
    name = raw.get("name", "")                 # a node name, or a tool name
    data = raw.get("data", {})                 # the event's payload

    if kind == "on_chain_start" and name in AGENTS:        # an agent started work
        agent_id, agent_name = AGENTS[name]                # look up its id + display name
        return {"t": "agent_start", "id": agent_id, "name": agent_name}   # tell the UI who started

    if kind == "on_chain_end" and name in AGENTS:          # an agent finished
        agent_id = AGENTS[name][0]                         # its short id
        verdict = (data.get("output") or {}).get(agent_id)   # the verdict it wrote into the state
        return {"t": "agent_done", "id": agent_id, "verdict": verdict}   # tell the UI it is done

    if kind == "on_tool_start" and current_agent:          # the agent is calling a tool
        return {"t": "tool_start", "id": current_agent, "tool": name, "args": data.get("input")}   # tell the UI which tool

    if kind == "on_tool_end" and current_agent:            # a tool returned a result
        return {"t": "tool_end", "id": current_agent, "tool": name, "out": _tool_output(data)}   # send the tidy result

    if kind == "on_chain_end" and name == "supervisor":    # the Chief Underwriter ruled
        out = data.get("output") or {}                     # the supervisor's output
        return {"t": "supervisor", "recommendation": out.get("recommendation"), "rationale": out.get("rationale")}   # send the ruling

    return None                                            # everything else — skip it
