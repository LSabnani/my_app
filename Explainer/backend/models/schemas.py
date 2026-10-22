"""Data schemas for Explainer multi-agent pipeline and CLEATS evaluation framework."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    PPT_DECK = "PPT_DECK"
    YOUTUBE_VIDEO = "YOUTUBE_VIDEO"
    ONLINE_DOCUMENT = "ONLINE_DOCUMENT"
    SCIENTIFIC_PAPER = "SCIENTIFIC_PAPER"


class SessionState(str, Enum):
    INTAKE = "INTAKE"
    BASELINE = "BASELINE"
    DEEP_DIVE = "DEEP_DIVE"
    EVALUATION = "EVALUATION"
    RECOMMENDATION = "RECOMMENDATION"


class UnmeasurableFlag(BaseModel):
    metric: str = Field(..., description="C, L, E, A, T, or S")
    name: str = Field(..., description="Full metric name e.g. Completeness")
    reason: str = Field(..., description="Why this dimension could not be measured")


class BKMStatus(BaseModel):
    is_bkm_eligible: bool = Field(
        ..., description="True if no metric is 0 and meets base thresholds"
    )
    is_elevated_bkm: bool = Field(
        ..., description="True if replicated by 3 people at 3 times with expected results"
    )
    disqualification_reason: Optional[str] = None
    triangulation_count: int = Field(default=0, description="Number of verified replications (out of 3)")
    triangulation_evidence: Optional[str] = None


class CLEATSScorecard(BaseModel):
    completeness: float = Field(..., ge=0, le=10, description="Completeness: coverage of question")
    latency: float = Field(..., ge=0, le=10, description="Latency: time/cognitive efficiency")
    engagement: float = Field(..., ge=0, le=10, description="Engagement: author & contributor breadth")
    accuracy: float = Field(..., ge=0, le=10, description="Accuracy: factual & competitive relevance")
    transparency: float = Field(..., ge=0, le=10, description="Transparency: reproducible method")
    standardization: float = Field(..., ge=0, le=10, description="Standardization: group/industry adoption")
    
    unmeasurable_flags: List[UnmeasurableFlag] = Field(default_factory=list)
    composite_score: float = Field(..., ge=0, le=10)
    bkm_status: BKMStatus
    is_simulated_data: bool = Field(default=False, description="Whether evaluated using user-approved simulated data")
    simulated_proposal_id: Optional[str] = Field(default=None, description="Traceback to simulated data agreement")
    scoring_rationale: Dict[str, str] = Field(default_factory=dict)


class ReferenceLink(BaseModel):
    title: str = Field(..., description="Display label for link")
    url: str = Field(..., description="Full verifiable URL")
    type: str = Field(..., description="document, website, or video")
    description: Optional[str] = None
    is_verified: bool = Field(default=True, description="Whether the critic verified the link is active")
    http_status: Optional[int] = Field(default=200, description="HTTP status code from critic check")
    verification_message: Optional[str] = Field(default="Critic Verified Active", description="Receipt note from critic link check")


class CandidateResource(BaseModel):
    id: str
    title: str
    url: str
    document_url: Optional[str] = Field(default=None, description="Direct link to slide deck or document (.ppt, .pdf)")
    website_url: Optional[str] = Field(default=None, description="Link to companion website, specs, or repo")
    video_url: Optional[str] = Field(default=None, description="Direct link to YouTube video walkthrough")
    reference_links: List[ReferenceLink] = Field(default_factory=list, description="All tracked verification links")
    type: ResourceType
    source: str
    author_or_channel: str
    snippet: str
    slide_count: Optional[int] = None
    video_duration: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier for academic paper")
    journal: Optional[str] = Field(default=None, description="Academic or scientific journal name")
    citation_count: Optional[int] = Field(default=None, description="Documented academic citations")
    tags: List[str] = Field(default_factory=list)
    scorecard: Optional[CLEATSScorecard] = None
    rank: Optional[int] = None
    critic_verified: bool = Field(default=True, description="Whether all candidate links passed the critic audit")
    critic_audit_notes: Optional[str] = Field(default=None, description="Critic link verification receipt notes")


class BaselinePrimer(BaseModel):
    source: str = "Wikipedia"
    topic: str
    summary_text: str
    page_url: Optional[str] = None
    confirmed: bool = False


class IntakeRequest(BaseModel):
    session_id: str
    problem: str
    intent: Optional[str] = ""
    target_application: Optional[str] = ""


class ConfirmPrimerRequest(BaseModel):
    session_id: str
    confirmed: bool
    refinement: Optional[str] = None


class ConfirmCandidatesRequest(BaseModel):
    session_id: str
    selected_ids: List[str]


class KnownEntity(BaseModel):
    category: str = Field(..., description="E.g. Conceptual Anchor, Architectural Pattern, Empirical Benchmark, Verified BKM")
    title: str
    detail: str
    confidence: float = Field(..., ge=0, le=10)
    primary_url: Optional[str] = Field(default=None, description="Direct clickable verification link")
    sources: List[str] = Field(default_factory=list)
    reference_links: List[ReferenceLink] = Field(default_factory=list, description="All verifiable clickable links")
    status: str = Field(default="VERIFIED", description="VERIFIED, CONSENSUS, or HIGH_CONFIDENCE")
    icon: str = "✓"
    critic_verified: bool = Field(default=True, description="Whether all reference links were checked by critic")


class UnknownStub(BaseModel):
    id: str
    category: str = Field(..., description="Unmeasured Metric, Replication Gap, Edge Case Boundary, Open Research")
    title: str
    gap_description: str
    impact_severity: str = Field(default="MEDIUM", description="HIGH, MEDIUM, or LOW")
    related_dimension: Optional[str] = None
    suggested_action: str
    inquiry_prompt: str = Field(..., description="Copy-pasteable targeted inquiry prompt")
    status: str = "OPEN_STUB"
    icon: str = "❓"


class KnowledgeInfographic(BaseModel):
    topic: str
    intent: Optional[str] = ""
    summary: str
    mastery_percentage: float = Field(..., ge=0, le=100)
    measured_dimensions_count: int
    unmeasured_stubs_count: int
    bkm_elevation_progress: str
    known_items: List[KnownEntity] = Field(default_factory=list)
    unknown_stubs: List[UnknownStub] = Field(default_factory=list)


class ExplainerSession(BaseModel):
    session_id: str
    state: SessionState = SessionState.INTAKE
    problem: Optional[str] = None
    intent: Optional[str] = None
    target_application: Optional[str] = None
    primer: Optional[BaselinePrimer] = None
    candidates: List[CandidateResource] = Field(default_factory=list)
    top3_recommendations: List[CandidateResource] = Field(default_factory=list)
    infographic: Optional[KnowledgeInfographic] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)


class SimulatedDataProposal(BaseModel):
    proposal_id: str = Field(..., description="Unique proposal identifier")
    topic: str
    candidate_id: str
    missing_data_description: str = Field(..., description="Explanation of missing test data")
    simulated_scenario: str = Field(..., description="Description of the proposed simulation")
    synthetic_metrics: Dict[str, Any] = Field(default_factory=dict, description="Proposed synthetic test parameters")
    rationale: str = Field(..., description="Why simulation is technically valid")
    user_agreed: bool = Field(default=False, description="Explicit user agreement flag")
    status: str = Field(default="PENDING_USER_AGREEMENT", description="PENDING_USER_AGREEMENT, USER_APPROVED, or USER_REJECTED")


class SimulatedDataConfirmationRequest(BaseModel):
    proposal_id: str
    user_agreed: bool


