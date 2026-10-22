"""FastAPI backend application for the Explainer PPT & Video Knowledge System."""
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models.schemas import (
    ExplainerSession,
    SessionState,
    IntakeRequest,
    ConfirmPrimerRequest,
    ConfirmCandidatesRequest,
    CandidateResource
)
from .agents.greeter_agent import GreeterAgent
from .agents.researcher_agent import ResearcherAgent
from .agents.evaluator_agent import EvaluatorAgent
from .services.bkm_service import BKMService
from .services.infographic_service import InfographicService
from .services.link_verifier import LinkVerifier

app = FastAPI(
    title="Explainer API",
    description="Multi-agent search, PPT/Video harvesting, and CLEATS evaluation engine",
    version="1.0.0"
)

# CORS setup for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".js", ".css", ".html")) or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Session memory store
sessions: Dict[str, ExplainerSession] = {}

# Agent instances
greeter = GreeterAgent()
researcher = ResearcherAgent()
evaluator = EvaluatorAgent()
bkm_service = BKMService()
infographic_service = InfographicService()
link_verifier = LinkVerifier()


@app.post("/api/session/start")
async def start_session():
    """Initializes a new session and returns the greeter intake prompt."""
    session_id = str(uuid.uuid4())[:8]
    session = ExplainerSession(session_id=session_id, state=SessionState.INTAKE)
    sessions[session_id] = session

    greeting_data = greeter.initial_greeting()
    session.history.append({
        "role": "agent",
        "agent": "Greeter",
        "message": greeting_data["message"],
        "suggested_topics": greeting_data["suggested_topics"]
    })

    return {
        "sessionId": session_id,
        "state": session.state,
        "greeting": greeting_data["message"],
        "suggestedTopics": greeting_data["suggested_topics"]
    }


@app.post("/api/chat/intake")
async def process_intake(req: IntakeRequest):
    """Processes user problem and motivation, retrieves baseline Wikipedia primer."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.problem = req.problem
    session.intent = req.intent
    session.target_application = req.target_application

    session.history.append({
        "role": "user",
        "message": req.problem,
        "intent": req.intent,
        "application": req.target_application
    })

    # Researcher fetches baseline Wikipedia primer
    primer = await researcher.get_primer(req.problem)
    session.primer = primer
    session.state = SessionState.BASELINE

    session.history.append({
        "role": "agent",
        "agent": "Researcher",
        "message": f"Retrieved baseline primer for '{primer.topic}'. Is this what you are interested in learning about?",
        "primer": primer.model_dump()
    })

    return {
        "sessionId": session.session_id,
        "state": session.state,
        "problem": session.problem,
        "primer": session.primer
    }


@app.post("/api/chat/confirm-primer")
async def confirm_primer(req: ConfirmPrimerRequest):
    """User confirms alignment on primer; triggers deep-dive search for PPTs and Videos."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not req.confirmed:
        # Refine scope
        if req.refinement:
            session.problem = req.refinement
            primer = await researcher.get_primer(req.refinement)
            session.primer = primer
            return {
                "sessionId": session.session_id,
                "state": SessionState.BASELINE,
                "refined": True,
                "primer": session.primer
            }
        else:
            session.state = SessionState.INTAKE
            return {"sessionId": session.session_id, "state": session.state}

    # User confirmed "Yes"
    if session.primer:
        session.primer.confirmed = True

    session.state = SessionState.DEEP_DIVE

    # Execute deep dive harvest
    topic = session.problem or "Distributed Systems"
    intent = session.intent or ""
    candidates = await researcher.execute_deep_dive(topic, intent)
    session.candidates = candidates

    session.history.append({
        "role": "agent",
        "agent": "Researcher",
        "message": f"Harvested {len(candidates)} slide decks, videos, and ScienceDirect peer-reviewed papers. Please review and confirm relevance.",
        "candidateCount": len(candidates)
    })

    return {
        "sessionId": session.session_id,
        "state": session.state,
        "candidates": session.candidates
    }


@app.post("/api/chat/confirm-candidates")
async def confirm_candidates(req: ConfirmCandidatesRequest):
    """User confirms relevance; Evaluator runs CLEATS scoring & selects Top 3."""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Filter candidates by selected IDs, or evaluate all if none specifically unchecked
    if req.selected_ids:
        eval_pool = [c for c in session.candidates if c.id in req.selected_ids]
    else:
        eval_pool = session.candidates

    if not eval_pool:
        eval_pool = session.candidates

    session.state = SessionState.EVALUATION

    # Run CLEATS Evaluation and rank Top 3 with Critic Link Audit
    top3 = await evaluator.rank_and_recommend(
        candidates=eval_pool,
        user_problem=session.problem or "",
        user_intent=session.intent or ""
    )

    session.top3_recommendations = top3
    session.infographic = infographic_service.generate_infographic(session)
    session.state = SessionState.RECOMMENDATION

    session.history.append({
        "role": "agent",
        "agent": "Critic (Evaluator)",
        "message": "Critic link audit and CLEATS evaluation complete. All published reference links verified active and valid.",
        "top3": [c.model_dump() for c in top3]
    })

    return {
        "sessionId": session.session_id,
        "state": session.state,
        "top3": session.top3_recommendations,
        "infographic": session.infographic
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve full session state and history."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/bkm/registry")
async def get_bkm_registry():
    """Retrieve verified Best Known Methods catalog."""
    return {"bkmTemplates": bkm_service.get_bkm_registry()}


@app.get("/api/session/{session_id}/infographic")
async def get_session_infographic(session_id: str):
    """Retrieve synthesized infographic of knowns and stubs for session."""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.infographic:
        session.infographic = infographic_service.generate_infographic(session)
    return session.infographic


@app.get("/api/infographic/topic/{topic}")
async def get_topic_infographic(topic: str, intent: str = ""):
    """Generate on-demand infographic of knowns and stubs for any topic."""
    return infographic_service.generate_topic_infographic(topic, intent)


@app.get("/api/link/verify")
async def verify_link(url: str):
    """Verify live reachability and status of a reference link."""
    return await link_verifier.verify_url(url)


@app.post("/api/link/verify-batch")
async def verify_links_batch(payload: Dict[str, list]):
    """Verify reachability of multiple reference URLs in batch."""
    urls = payload.get("urls", [])
    results = await link_verifier.verify_batch(urls)
    return {"results": results}


# Simulated Data Proposals store for User Agreement Gate
simulated_proposals: Dict[str, Any] = {}


@app.post("/api/critic/simulated-data/propose")
async def propose_simulated_data(payload: Dict[str, Any]):
    """Critic proposes simulated test data when empirical data is missing or unmeasurable."""
    candidate_id = payload.get("candidate_id", "cand_01")
    topic = payload.get("topic", "System Architecture")
    missing_reason = payload.get("missing_reason", "Empirical tail latency benchmark telemetry is unavailable.")
    
    # Create provisional candidate representation for proposal
    candidate = CandidateResource(
        id=candidate_id,
        title=payload.get("title", f"Candidate {candidate_id}"),
        url="https://en.wikipedia.org/wiki/OAuth",
        type="ONLINE_DOCUMENT",
        source="Engineering Domain",
        author_or_channel="Practitioner",
        snippet="Provisional candidate requiring simulated workload data."
    )
    proposal = evaluator.propose_simulated_data(
        candidate=candidate,
        missing_data_description=missing_reason,
        topic=topic
    )
    simulated_proposals[proposal.proposal_id] = proposal
    return proposal


@app.post("/api/critic/simulated-data/confirm")
async def confirm_simulated_data(payload: Dict[str, Any]):
    """User Agreement Gate: Confirm or reject Critic's proposed simulated test data."""
    proposal_id = payload.get("proposal_id")
    user_agreed = payload.get("user_agreed", False)
    session_id = payload.get("session_id")
    
    if not proposal_id or proposal_id not in simulated_proposals:
        raise HTTPException(status_code=404, detail="Simulated data proposal not found")
        
    proposal = simulated_proposals[proposal_id]
    proposal.user_agreed = user_agreed
    proposal.status = "USER_APPROVED" if user_agreed else "USER_REJECTED"
    
    updated_candidate = None
    if session_id and session_id in sessions:
        session = sessions[session_id]
        # Look for target candidate across top3 or candidate pool
        target = next((c for c in session.top3_recommendations if c.id == proposal.candidate_id), None)
        if not target:
            target = next((c for c in session.candidates if c.id == proposal.candidate_id), None)
        
        if user_agreed:
            if target:
                new_scorecard = evaluator.evaluate_resource(
                    candidate=target,
                    user_problem=session.problem or "",
                    user_intent=session.intent or "",
                    simulated_data_proposal=proposal
                )
                target.scorecard = new_scorecard
                updated_candidate = target
        else:
            # User declined simulated data: Add an exploration stub to the infographic
            if session.infographic:
                from backend.models.schemas import UnknownStub
                stub_id = f"stub_declined_sim_{proposal.candidate_id}"
                if not any(s.id == stub_id for s in session.infographic.unknown_stubs):
                    session.infographic.unknown_stubs.append(
                        UnknownStub(
                            id=stub_id,
                            category="Unmeasured Metric",
                            title=f"Empirical Benchmark Gap: {proposal.topic}",
                            gap_description=f"Simulation declined by user. Empirical benchmark for '{proposal.missing_data_description}' remains unmeasured.",
                            impact_severity="HIGH",
                            related_dimension="Standardization",
                            suggested_action="Deploy automated production telemetry probes to capture live empirical latency traces.",
                            inquiry_prompt=f"Investigate empirical benchmarks for {proposal.topic}: {proposal.missing_data_description}"
                        )
                    )
                    session.infographic.unmeasured_stubs_count = len(session.infographic.unknown_stubs)
    
    return {
        "proposal_id": proposal_id,
        "status": proposal.status,
        "proceed_with_test": user_agreed,
        "proposal": proposal,
        "updated_candidate": updated_candidate
    }



# Mount GUI frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
