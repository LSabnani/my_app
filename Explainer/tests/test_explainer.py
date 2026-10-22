"""Unit tests for the Explainer backend multi-agent pipeline and CLEATS scoring."""
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.agents.greeter_agent import GreeterAgent
from backend.agents.researcher_agent import ResearcherAgent
from backend.agents.evaluator_agent import EvaluatorAgent
from backend.services.bkm_service import BKMService
from backend.models.schemas import CandidateResource, ResourceType

client = TestClient(app)


def test_greeter_agent():
    greeter = GreeterAgent()
    greeting = greeter.initial_greeting()
    assert "What is the problem" in greeting["message"]
    assert len(greeting["suggested_topics"]) > 0

    intake = greeter.process_intake("Understanding Kubernetes Ingress")
    assert intake["problem"] == "Understanding Kubernetes Ingress"
    assert intake["intent"] is not None


@pytest.mark.asyncio
async def test_researcher_agent_primer():
    researcher = ResearcherAgent()
    primer = await researcher.get_primer("Distributed Computing")
    assert primer.topic is not None
    assert len(primer.summary_text) > 0


@pytest.mark.asyncio
async def test_researcher_deep_dive():
    researcher = ResearcherAgent()
    candidates = await researcher.execute_deep_dive("Machine Learning")
    assert len(candidates) > 0
    # Must include PPT decks, YouTube videos, and ScienceDirect peer-reviewed papers
    types = {c.type for c in candidates}
    assert ResourceType.PPT_DECK in types
    assert ResourceType.YOUTUBE_VIDEO in types
    assert ResourceType.SCIENTIFIC_PAPER in types
    
    # Must track links for documents, websites, and videos
    for c in candidates:
        assert c.url is not None
        assert len(c.reference_links) > 0
        link_types = {link.type for link in c.reference_links}
        assert ("document" in link_types or "video" in link_types or "website" in link_types)


def test_evaluator_cleats_and_bkm():
    evaluator = EvaluatorAgent()
    
    # Candidate with valid metadata
    c1 = CandidateResource(
        id="c1",
        title="Production Microservices: Enterprise BKM Template",
        url="https://example.com/ppt",
        type=ResourceType.PPT_DECK,
        source="Open Infrastructure Foundation",
        author_or_channel="Lead Architecture Guild",
        snippet="Standardized presentation template",
        slide_count=20,
        tags=["Slide Deck", "BKM Ready", "Standardization"]
    )
    scorecard = evaluator.evaluate_resource(c1, "Microservices architecture")
    
    assert scorecard.completeness > 0
    assert scorecard.latency > 0
    assert scorecard.engagement > 0
    assert scorecard.accuracy > 0
    assert scorecard.transparency > 0
    assert scorecard.standardization > 0
    assert scorecard.composite_score > 0
    assert scorecard.bkm_status.is_bkm_eligible is True


def test_evaluator_sciencedirect_paper():
    evaluator = EvaluatorAgent()
    paper = CandidateResource(
        id="sd_test_01",
        title="Systematic Review & Architectural Taxonomy: Production Microservices",
        url="https://www.sciencedirect.com/science/article/pii/S138376212401234X",
        document_url="https://www.sciencedirect.com/science/article/pii/S138376212401234X/pdfft",
        website_url="https://doi.org/10.1016/j.sysarc.2024.101234",
        type=ResourceType.SCIENTIFIC_PAPER,
        source="ScienceDirect (Journal of Systems Architecture)",
        author_or_channel="Prof. S. R. Thorne & Research Group",
        snippet="Comprehensive peer-reviewed literature review with quantitative latency benchmarks.",
        doi="10.1016/j.sysarc.2024.101234",
        journal="Journal of Systems Architecture",
        citation_count=142,
        tags=["ScienceDirect", "Peer-Reviewed", "Systematic Review", "BKM Ready"]
    )
    scorecard = evaluator.evaluate_resource(paper, "Production Microservices")
    
    assert scorecard.completeness >= 9.0
    assert scorecard.accuracy >= 9.5
    assert scorecard.transparency >= 9.0
    assert scorecard.standardization >= 9.0
    assert scorecard.bkm_status.is_bkm_eligible is True
    assert scorecard.composite_score > 8.5



def test_zero_penalty_rule():
    bkm_service = BKMService()
    # If unmeasurable count > 0 or any metric is 0, BKM is strictly disqualified
    bkm_status = bkm_service.evaluate_bkm_eligibility(
        completeness=9.0,
        latency=8.5,
        engagement=9.0,
        accuracy=9.0,
        transparency=9.0,
        standardization=0.0, # Zero score
        unmeasurable_count=1
    )
    assert bkm_status.is_bkm_eligible is False
    assert "ZERO" in bkm_status.disqualification_reason


def test_api_session_lifecycle():
    # 1. Start session
    start_resp = client.post("/api/session/start")
    assert start_resp.status_code == 200
    session_id = start_resp.json()["sessionId"]
    assert session_id is not None

    # 2. Intake problem
    intake_resp = client.post("/api/chat/intake", json={
        "session_id": session_id,
        "problem": "Kubernetes Architecture",
        "intent": "Production rollout",
        "target_application": "System design review"
    })
    assert intake_resp.status_code == 200
    assert intake_resp.json()["state"] == "BASELINE"
    assert "primer" in intake_resp.json()

    # 3. Confirm primer (triggers PPT & video harvesting)
    confirm_primer_resp = client.post("/api/chat/confirm-primer", json={
        "session_id": session_id,
        "confirmed": True
    })
    assert confirm_primer_resp.status_code == 200
    candidates = confirm_primer_resp.json()["candidates"]
    assert len(candidates) >= 3

    # 4. Confirm candidates (triggers CLEATS evaluation & Top 3)
    confirm_cand_resp = client.post("/api/chat/confirm-candidates", json={
        "session_id": session_id,
        "selected_ids": [c["id"] for c in candidates[:4]]
    })
    assert confirm_cand_resp.status_code == 200
    top3 = confirm_cand_resp.json()["top3"]
    assert len(top3) <= 3
    assert len(top3) > 0
    assert top3[0]["scorecard"] is not None
    assert top3[0]["scorecard"]["composite_score"] > 0
    # Assert links are always present in recommendations for validation
    assert len(top3[0]["reference_links"]) > 0
    assert (top3[0].get("document_url") or top3[0].get("video_url") or top3[0].get("website_url")) is not None
    # 5. Assert Infographic with known items and unknown stubs was synthesized
    assert "infographic" in confirm_cand_resp.json()
    infographic = confirm_cand_resp.json()["infographic"]
    assert len(infographic["known_items"]) > 0
    assert len(infographic["unknown_stubs"]) > 0
    assert infographic["mastery_percentage"] > 0


def test_knowledge_infographic_and_stubs():
    from backend.services.infographic_service import InfographicService
    service = InfographicService()
    info = service.generate_topic_infographic("OAuth2 PKCE Flow", "Mobile Security")
    
    assert info.topic == "OAuth2 PKCE Flow"
    assert len(info.known_items) >= 4
    assert len(info.unknown_stubs) >= 3
    assert info.mastery_percentage > 0
    
    # Check that stubs have actionable prompt and severity
    for stub in info.unknown_stubs:
        assert stub.id is not None
        assert stub.inquiry_prompt is not None
        assert len(stub.inquiry_prompt) > 10
        assert stub.impact_severity in ["HIGH", "MEDIUM", "LOW"]

    # Check that known items have verifiable clickable reference links
    for item in info.known_items:
        assert item.primary_url is not None
        assert item.primary_url.startswith("http://") or item.primary_url.startswith("https://")
        assert len(item.reference_links) >= 1
        for link in item.reference_links:
            assert link.title is not None
            assert link.url.startswith("http://") or link.url.startswith("https://")
            assert link.type in ["website", "document", "video", "paper"]

    # Test API endpoint
    resp = client.get("/api/infographic/topic/Transformer%20Attention%20Mechanisms")
    assert resp.status_code == 200
    data = resp.json()
    assert "known_items" in data
    assert "unknown_stubs" in data
    # Verify API serializes reference_links
    for k in data["known_items"]:
        assert "reference_links" in k
        assert len(k["reference_links"]) >= 1


@pytest.mark.asyncio
async def test_link_verifiability_cable_manufacturing():
    """Verify that all generated links for cable manufacturing should cost model are verifiable and active."""
    researcher = ResearcherAgent()
    topic = "cable manufacturing should cost model"
    candidates = await researcher.execute_deep_dive(topic)
    
    assert len(candidates) > 0
    for c in candidates:
        # Guarantee no fabricated dummy paths ending in fake .pptx
        assert not (c.document_url and c.document_url.endswith("-architecture-deepdive.pptx"))
        assert not (c.video_url and "watch?v=explainer_" in c.video_url)
        assert not (c.document_url and "techexplainerlabs.com" in c.document_url)

        # Check all reference links are formatted properly
        for link in c.reference_links:
            assert link.url.startswith("http://") or link.url.startswith("https://")
            assert not link.url.endswith("-architecture-deepdive.pptx")
            assert "techexplainerlabs.com" not in link.url
            assert not link.url.endswith("template.pptx")


@pytest.mark.asyncio
async def test_link_verifier_service_and_api():
    """Test the LinkVerifier service and /api/link/verify endpoint."""
    from backend.services.link_verifier import LinkVerifier
    verifier = LinkVerifier()

    # Valid search URL
    res = await verifier.verify_url("https://www.slideshare.net/search?q=cable+manufacturing")
    assert res["verifiable"] is True

    # Bad scheme or empty
    bad_res = await verifier.verify_url("not_a_url")
    assert bad_res["verifiable"] is False

    # Test API endpoint
    resp = client.get("/api/link/verify?url=https://ocw.mit.edu/search/?q=manufacturing")
    assert resp.status_code == 200
    assert "verifiable" in resp.json()


@pytest.mark.asyncio
async def test_critic_link_check_before_publishing():
    """Verify that CriticAgent / EvaluatorAgent checks links before publishing and penalizes dead links."""
    from backend.agents.evaluator_agent import CriticAgent
    from backend.models.schemas import CandidateResource, ResourceType, ReferenceLink

    critic = CriticAgent()

    # 1. Candidate with a fake/broken link
    broken_candidate = CandidateResource(
        id="broken_cand_01",
        title="Architecture with Dead Links",
        url="https://invalid-non-existent-domain-99999999.org",
        document_url="https://invalid-non-existent-domain-99999999.org/deck.pdf",
        type=ResourceType.PPT_DECK,
        source="Unverified Source",
        author_or_channel="Anonymous",
        snippet="Presentation with broken reference links",
        slide_count=20,
        tags=["Slide Deck", "Architecture"],
        reference_links=[
            ReferenceLink(
                title="Broken Presentation Link",
                url="https://invalid-non-existent-domain-99999999.org/deck.pdf",
                type="document"
            )
        ]
    )

    # 2. Candidate with a valid active link
    valid_candidate = CandidateResource(
        id="valid_cand_02",
        title="Architecture with Verified Active Links",
        url="https://www.slideshare.net/search?q=architecture",
        document_url="https://www.slideshare.net/search?q=architecture",
        type=ResourceType.PPT_DECK,
        source="SlideShare Technical Decks",
        author_or_channel="Enterprise Architecture Guild",
        snippet="Valid presentation with active links",
        slide_count=20,
        tags=["Slide Deck", "Architecture", "BKM Ready", "Standardization"],
        reference_links=[
            ReferenceLink(
                title="SlideShare Architecture Slide Decks",
                url="https://www.slideshare.net/search?q=architecture",
                type="document"
            )
        ]
    )

    # Run Critic rank and recommend
    published_top = await critic.rank_and_recommend(
        candidates=[broken_candidate, valid_candidate],
        user_problem="Cloud Architecture"
    )

    # Verify that valid candidate is published as Rank #1
    assert len(published_top) >= 1
    top_resource = published_top[0]
    assert top_resource.id == "valid_cand_02"
    assert top_resource.critic_verified is True
    assert top_resource.scorecard.transparency > 0
    assert top_resource.scorecard.bkm_status.is_bkm_eligible is True

    # Check that broken candidate has Transparency = 0.0 under CLEATS Zero-Penalty rule
    for r in published_top:
        if r.id == "broken_cand_01":
            assert r.critic_verified is False
            assert r.scorecard.transparency == 0.0
            assert r.scorecard.bkm_status.is_bkm_eligible is False
            assert any(f.metric == "T" for f in r.scorecard.unmeasurable_flags)


@pytest.mark.asyncio
async def test_critic_circumstance_1_healthy_links():
    """
    Circumstance 1: All Links 100% Active & Reachable
    What Must Go Right:
    - Pre-publication active link verification succeeds on all candidate URLs.
    - Transparency is awarded full score (>= 8.5).
    - Zero unmeasurable flags.
    - Candidate qualifies for Best Known Method (BKM).
    - Published as Rank #1 recommendation.
    - Residual RPN = 0.
    """
    from backend.agents.evaluator_agent import CriticAgent
    from backend.models.schemas import CandidateResource, ResourceType, ReferenceLink
    from backend.services.link_verifier import LinkVerifier

    critic = CriticAgent()
    verifier = LinkVerifier()

    healthy_candidate = CandidateResource(
        id="healthy_cand_01",
        title="Enterprise PKCE Authentication Architecture",
        url="https://en.wikipedia.org/wiki/OAuth",
        document_url="https://en.wikipedia.org/wiki/OAuth",
        type=ResourceType.PPT_DECK,
        source="IETF OAuth Working Group",
        author_or_channel="Security Standards Guild",
        snippet="Standardized architecture for OAuth 2.0 PKCE flow.",
        slide_count=22,
        tags=["Slide Deck", "Architecture", "BKM Ready", "Standardization"],
        reference_links=[
            ReferenceLink(
                title="Wikipedia OAuth Specification",
                url="https://en.wikipedia.org/wiki/OAuth",
                type="document"
            ),
            ReferenceLink(
                title="IETF RFC 7636",
                url="https://en.wikipedia.org/wiki/Proof_Key_for_Code_Exchange",
                type="website"
            )
        ]
    )

    # 1. Verify links directly via LinkVerifier
    for link in healthy_candidate.reference_links:
        res = await verifier.verify_url(link.url)
        assert res["verifiable"] is True
        assert res["rpn"] == 0
        assert res["severity"] == 0
        assert res["detectability"] == 1
        assert "Verified active endpoint" in res["tell_tale_signs"]

    # 2. Critic rank and recommend
    top_published = await critic.rank_and_recommend(
        candidates=[healthy_candidate],
        user_problem="OAuth2 PKCE Architecture"
    )

    assert len(top_published) == 1
    rec = top_published[0]
    assert rec.rank == 1
    assert rec.critic_verified is True
    assert rec.scorecard.transparency >= 8.5
    assert len(rec.scorecard.unmeasurable_flags) == 0
    assert rec.scorecard.bkm_status.is_bkm_eligible is True
    assert "Critic Link Audit PASSED" in rec.critic_audit_notes


@pytest.mark.asyncio
async def test_critic_circumstance_2_subtle_nested_broken_link():
    """
    Circumstance 2: Subtle Deep Broken Link in Reference Array
    What Must Go Right:
    - Primary candidate URL resolves, but secondary/nested reference link 404s.
    - Critic catches the nested failure before publication.
    - Transparency is strictly scored as 0.0 (CLEATS Zero-Penalty).
    - Unmeasurable flag is attached explaining dead link.
    - Candidate is disqualified from BKM elevation.
    - Gated from Rank #1 when competing with a verified candidate.
    - Risk analysis reports RPN = 336 (S=8, O=6, D=7) and tell-tale signs.
    """
    from backend.agents.evaluator_agent import CriticAgent
    from backend.models.schemas import CandidateResource, ResourceType, ReferenceLink
    from backend.services.link_verifier import LinkVerifier

    critic = CriticAgent()
    verifier = LinkVerifier()

    # Broken URL representing synthetic/hallucinated slide deck
    dead_url = "https://invalid-non-existent-domain-99999999.org/cable-manufacturing-should-cost-model-architecture-deepdive.pptx"

    # Verify RPN and tell-tale signs for dead URL
    res = await verifier.verify_url(dead_url)
    assert res["verifiable"] is False
    assert res["severity"] == 8       # $500k-$1.5M contract loss
    assert res["occurrence"] == 6     # Frequent in hallucinated links
    assert res["detectability"] == 7  # Syntactically looks like a valid .pptx link
    assert res["rpn"] == 336          # 8 * 6 * 7
    assert "Server returned HTTP" in res["tell_tale_signs"] or "DNS failure" in res["tell_tale_signs"]

    # Candidate with valid primary URL, but subtle nested dead reference link
    nested_broken_candidate = CandidateResource(
        id="cand_nested_broken_02",
        title="Cost Modeling with Nested Dead Citation",
        url="https://en.wikipedia.org/wiki/OAuth",
        document_url="https://en.wikipedia.org/wiki/OAuth",
        type=ResourceType.PPT_DECK,
        source="Cost Engineering Guild",
        author_or_channel="Practitioner",
        snippet="Manufacturing cost model with broken reference deck.",
        slide_count=25,
        tags=["Slide Deck", "Architecture", "BKM Ready"],
        reference_links=[
            ReferenceLink(
                title="Active Conceptual Anchor",
                url="https://en.wikipedia.org/wiki/OAuth",
                type="website"
            ),
            ReferenceLink(
                title="Dead Deep-Dive Presentation",
                url=dead_url,
                type="document"
            )
        ]
    )

    healthy_candidate = CandidateResource(
        id="cand_healthy_competing_02",
        title="Fully Verified Cost Architecture",
        url="https://en.wikipedia.org/wiki/OAuth",
        document_url="https://en.wikipedia.org/wiki/OAuth",
        type=ResourceType.PPT_DECK,
        source="Verified Cost Guild",
        author_or_channel="Principal Architect",
        snippet="All reference links fully active and verified.",
        slide_count=20,
        tags=["Slide Deck", "Architecture", "BKM Ready", "Standardization"],
        reference_links=[
            ReferenceLink(
                title="Active Reference",
                url="https://en.wikipedia.org/wiki/OAuth",
                type="website"
            )
        ]
    )

    # Run Critic rank and recommend
    top_published = await critic.rank_and_recommend(
        candidates=[nested_broken_candidate, healthy_candidate],
        user_problem="Should Cost Modeling"
    )

    assert len(top_published) >= 1
    # Healthy candidate must be elevated to Rank #1
    assert top_published[0].id == "cand_healthy_competing_02"
    assert top_published[0].rank == 1
    assert top_published[0].critic_verified is True

    # Nested broken candidate must be penalized and disqualified from BKM
    broken_rec = next(r for r in top_published if r.id == "cand_nested_broken_02")
    assert broken_rec.critic_verified is False
    assert broken_rec.scorecard.transparency == 0.0
    assert broken_rec.scorecard.bkm_status.is_bkm_eligible is False
    assert any(f.metric == "T" for f in broken_rec.scorecard.unmeasurable_flags)
    assert "dead/unverifiable reference link detected" in broken_rec.scorecard.unmeasurable_flags[0].reason


@pytest.mark.asyncio
async def test_critic_circumstance_3_soft_404_and_bot_shield():
    """
    Circumstance 3: Bot-Shielded Institutional Domain & Soft-404 Masking
    What Must Go Right:
    - Institutional publisher bot defenses (HTTP 401/403 Cloudflare on ScienceDirect) are recognized as active publishers, not penalized.
    - Soft-404 (HTTP 200 returned, but page body contains 'Presentation not found' / 'Item has been removed') is detected via content inspection.
    - Soft-404 gets higher lack-of-detectability score (D=9 vs D=7), producing RPN = 315 (S=7, O=5, D=9).
    - Soft-404 candidate is flagged critic_verified = False with Transparency = 0.0.
    """
    from unittest.mock import patch, AsyncMock
    from backend.agents.evaluator_agent import CriticAgent
    from backend.models.schemas import CandidateResource, ResourceType, ReferenceLink
    from backend.services.link_verifier import LinkVerifier

    verifier = LinkVerifier()
    critic = CriticAgent()

    # Part A: Test Bot-Shield handling (HTTP 403 on ScienceDirect/Elsevier)
    # Institutional publishers block automated HEAD/GET with 403 Forbidden, but are active
    mock_resp_403 = AsyncMock()
    mock_resp_403.status_code = 403

    with patch("httpx.AsyncClient.head", new_callable=AsyncMock) as mock_head:
        mock_head.return_value = mock_resp_403
        res_shield = await verifier.verify_url("https://www.sciencedirect.com/science/article/pii/S0950705121000552")
        assert res_shield["verifiable"] is True
        assert res_shield["status_code"] == 403
        assert res_shield["rpn"] == 0

    # Part B: Test Soft-404 handling (HTTP 200 returned, but body contains removal text)
    mock_resp_soft_404 = AsyncMock()
    mock_resp_soft_404.status_code = 200
    mock_resp_soft_404.text = "<html><body><h1>Presentation Not Found</h1><p>This content has been removed by the author.</p></body></html>"

    with patch("httpx.AsyncClient.head", new_callable=AsyncMock) as mock_head, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_head.return_value = mock_resp_soft_404
        mock_get.return_value = mock_resp_soft_404

        res_soft = await verifier.verify_url("https://www.slideshare.net/slideshow/removed-presentation-12345")
        # Soft 404 must be marked unverified despite status 200
        assert res_soft["verifiable"] is False
        assert "Soft-404" in res_soft["reason"]
        # Lack of detectability gets a HIGHER score (D=9) because HTTP status was 200
        assert res_soft["detectability"] == 9
        assert res_soft["severity"] == 7      # $100k-$450k downtime
        assert res_soft["occurrence"] == 5    # Legacy platform deletion frequency
        assert res_soft["rpn"] == 315         # 7 * 5 * 9
        assert "HTML payload" in res_soft["tell_tale_signs"]

    # Part C: Full CriticAgent evaluation with a candidate having a soft-404 reference link
    soft_404_candidate = CandidateResource(
        id="cand_soft_404_03",
        title="Legacy Slide Deck with Soft-404",
        url="https://www.slideshare.net/slideshow/removed-presentation-12345",
        document_url="https://www.slideshare.net/slideshow/removed-presentation-12345",
        type=ResourceType.PPT_DECK,
        source="Legacy Slides Portal",
        author_or_channel="Former Employee",
        snippet="Presentation that was removed but server still serves 200 page.",
        slide_count=18,
        tags=["Slide Deck"],
        reference_links=[
            ReferenceLink(
                title="Removed Slide Deck",
                url="https://www.slideshare.net/slideshow/removed-presentation-12345",
                type="document"
            )
        ]
    )

    with patch("httpx.AsyncClient.head", new_callable=AsyncMock) as mock_head, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_head.return_value = mock_resp_soft_404
        mock_get.return_value = mock_resp_soft_404

        top_published = await critic.rank_and_recommend(
            candidates=[soft_404_candidate],
            user_problem="Legacy Systems"
        )

        assert len(top_published) == 1
        rec = top_published[0]
        assert rec.critic_verified is False
        assert rec.scorecard.transparency == 0.0
        assert rec.scorecard.bkm_status.is_bkm_eligible is False
        assert any("Soft-404" in f.reason or "dead/unverifiable" in f.reason for f in rec.scorecard.unmeasurable_flags)


def test_critic_propose_simulated_data_and_user_agreement_gate():
    """
    Test Critic Simulated Data Protocol:
    1. If test data is not available, critic proposes simulated data.
    2. Without user agreement, proceeding with test is blocked (PermissionError).
    3. After user agreement, test proceeds with clear simulated provenance.
    """
    import pytest
    from backend.agents.evaluator_agent import CriticAgent
    from backend.models.schemas import CandidateResource, ResourceType

    critic = CriticAgent()

    candidate = CandidateResource(
        id="cand_missing_data_01",
        title="High-Scale Edge Routing Architecture",
        url="https://en.wikipedia.org/wiki/OAuth",
        type=ResourceType.ONLINE_DOCUMENT,
        source="Distributed Systems Guild",
        author_or_channel="Principal Architect",
        snippet="Novel routing architecture with unmeasured empirical telemetry under 50k QPS."
    )

    # 1. When empirical test data is unavailable, critic proposes simulated data
    missing_desc = "Empirical p99 tail latency under 50,000 QPS edge saturation"
    proposal = critic.propose_simulated_data(
        candidate=candidate,
        missing_data_description=missing_desc,
        topic="Edge Routing Telemetry"
    )

    assert proposal.proposal_id.startswith("sim_prop_")
    assert proposal.missing_data_description == missing_desc
    assert proposal.user_agreed is False
    assert proposal.status == "PENDING_USER_AGREEMENT"
    assert "workload_distribution" in proposal.synthetic_metrics
    assert len(proposal.rationale) > 20

    # 2. Critic MUST NOT proceed without explicit user agreement
    with pytest.raises(PermissionError) as exc_info:
        critic.evaluate_resource(
            candidate=candidate,
            user_problem="High Scale Routing",
            simulated_data_proposal=proposal
        )
    assert "User Agreement Gate" in str(exc_info.value)

    # 3. User agrees to the proposal
    proposal.user_agreed = True
    proposal.status = "USER_APPROVED"

    # 4. Now the test proceeds with user agreement
    scorecard = critic.evaluate_resource(
        candidate=candidate,
        user_problem="High Scale Routing",
        simulated_data_proposal=proposal
    )

    assert scorecard.is_simulated_data is True
    assert scorecard.simulated_proposal_id == proposal.proposal_id
    assert "simulated_data_provenance" in scorecard.scoring_rationale
    assert "[USER-APPROVED SIMULATED DATA PROVENANCE" in scorecard.scoring_rationale["simulated_data_provenance"]
    # Simulated data cannot unilaterally elevate to empirical BKM
    assert scorecard.bkm_status.is_elevated_bkm is False
    assert "Simulated data cannot unilaterally elevate" in scorecard.bkm_status.disqualification_reason


def test_simulated_data_api_endpoints():
    """Test the /api/critic/simulated-data/propose and /api/critic/simulated-data/confirm endpoints."""
    # 1. Propose simulated data
    propose_resp = client.post("/api/critic/simulated-data/propose", json={
        "candidate_id": "cand_api_test",
        "topic": "Microservice Distributed Tracing",
        "missing_reason": "Field telemetry for cross-region partition missing"
    })
    assert propose_resp.status_code == 200
    proposal = propose_resp.json()
    assert "proposal_id" in proposal
    assert proposal["status"] == "PENDING_USER_AGREEMENT"
    assert proposal["user_agreed"] is False

    # 2. Confirm rejection
    reject_resp = client.post("/api/critic/simulated-data/confirm", json={
        "proposal_id": proposal["proposal_id"],
        "user_agreed": False
    })
    assert reject_resp.status_code == 200
    reject_data = reject_resp.json()
    assert reject_data["status"] == "USER_REJECTED"
    assert reject_data["proceed_with_test"] is False

    # 3. Confirm agreement
    confirm_resp = client.post("/api/critic/simulated-data/confirm", json={
        "proposal_id": proposal["proposal_id"],
        "user_agreed": True
    })
    assert confirm_resp.status_code == 200
    confirm_data = confirm_resp.json()
    assert confirm_data["status"] == "USER_APPROVED"
    assert confirm_data["proceed_with_test"] is True


def test_simulated_data_session_confirmation_and_stub_flow():
    """Verify session-level candidate re-evaluation on simulation approval and stub creation on decline."""
    # 1. Start session & progress to candidates
    start_resp = client.post("/api/session/start")
    session_id = start_resp.json()["sessionId"]

    client.post("/api/chat/intake", json={
        "session_id": session_id,
        "problem": "Asynchronous Event Sourcing"
    })
    client.post("/api/chat/confirm-primer", json={
        "session_id": session_id,
        "confirmed": True
    })
    cand_resp = client.post("/api/chat/confirm-candidates", json={
        "session_id": session_id,
        "selected_ids": []
    })
    assert cand_resp.status_code == 200
    top3 = cand_resp.json()["top3"]
    assert len(top3) > 0
    target_cand_id = top3[0]["id"]

    # 2. Propose simulated data for top candidate
    propose_resp = client.post("/api/critic/simulated-data/propose", json={
        "candidate_id": target_cand_id,
        "topic": "Event Sourcing Partition",
        "missing_reason": "Live chaos partition telemetry is unavailable"
    })
    proposal = propose_resp.json()
    proposal_id = proposal["proposal_id"]

    # 3. Confirm with user agreement + session_id -> Re-evaluation happens
    confirm_resp = client.post("/api/critic/simulated-data/confirm", json={
        "proposal_id": proposal_id,
        "user_agreed": True,
        "session_id": session_id
    })
    assert confirm_resp.status_code == 200
    data = confirm_resp.json()
    assert data["status"] == "USER_APPROVED"
    assert data["updated_candidate"] is not None
    assert data["updated_candidate"]["scorecard"]["is_simulated_data"] is True
    assert data["updated_candidate"]["scorecard"]["simulated_proposal_id"] == proposal_id

    # 4. Propose another simulation and decline -> Stub added to infographic
    prop_decline = client.post("/api/critic/simulated-data/propose", json={
        "candidate_id": "cand_declined_test",
        "topic": "Unmeasured Edge Partition",
        "missing_reason": "Missing edge partition failure metrics"
    }).json()

    decline_resp = client.post("/api/critic/simulated-data/confirm", json={
        "proposal_id": prop_decline["proposal_id"],
        "user_agreed": False,
        "session_id": session_id
    })
    assert decline_resp.status_code == 200
    decline_data = decline_resp.json()
    assert decline_data["status"] == "USER_REJECTED"

    # Check infographic has the exploration stub
    info_resp = client.get(f"/api/session/{session_id}/infographic")
    assert info_resp.status_code == 200
    infographic = info_resp.json()
    assert any("stub_declined_sim_" in s["id"] for s in infographic["unknown_stubs"])







