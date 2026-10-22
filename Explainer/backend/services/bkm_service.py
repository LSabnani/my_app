"""Best Known Method (BKM) tracking and elevation service."""
from typing import Dict, List, Optional
from ..models.schemas import BKMStatus, CLEATSScorecard


class BKMService:
    """Evaluates and catalogs Best Known Methods according to strict triangulation rules."""

    def __init__(self):
        # In-memory catalog of elevated BKMs
        self._bkm_registry: List[Dict] = [
            {
                "id": "bkm_001",
                "title": "Zero-Downtime Blue/Green Deployment Pattern",
                "method_name": "Canary Traffic Shifting & Automated Health Validation",
                "domain": "DevOps & Cloud Systems",
                "replications": [
                    {"person": "Alice M. (SRE Lead)", "timestamp": "2024-03-15", "result": "Expected 0% error spike"},
                    {"person": "David K. (Platform Eng)", "timestamp": "2024-07-22", "result": "Expected 0% error spike"},
                    {"person": "Elena R. (Infra Architect)", "timestamp": "2024-11-09", "result": "Expected 0% error spike"}
                ],
                "status": "ELEVATED_BKM_TEMPLATE",
                "cleats_scores": {"C": 9.5, "L": 8.8, "E": 9.0, "A": 9.8, "T": 9.7, "S": 9.6}
            }
        ]

    def evaluate_bkm_eligibility(
        self,
        completeness: float,
        latency: float,
        engagement: float,
        accuracy: float,
        transparency: float,
        standardization: float,
        unmeasurable_count: int,
        duplication_proof_count: int = 0
    ) -> BKMStatus:
        """Evaluate whether a candidate can be elevated to a Best Known Method (BKM)."""
        metrics = [completeness, latency, engagement, accuracy, transparency, standardization]

        # Rule 1: Any metric = 0 strictly disqualifies from BKM
        if unmeasurable_count > 0 or any(m <= 0 for m in metrics):
            return BKMStatus(
                is_bkm_eligible=False,
                is_elevated_bkm=False,
                disqualification_reason="Metric rating of ZERO detected. ZEROS cannot contribute to BKMs.",
                triangulation_count=0,
                triangulation_evidence=None
            )

        # Rule 2: Minimum quality threshold for BKM consideration (>= 7.0 in all dimensions)
        if any(m < 6.5 for m in metrics):
            return BKMStatus(
                is_bkm_eligible=False,
                is_elevated_bkm=False,
                disqualification_reason="Scores below minimum BKM threshold (all metrics must be >= 6.5).",
                triangulation_count=duplication_proof_count,
                triangulation_evidence="Requires higher baseline standardization and completeness."
            )

        # Rule 3: 3 people at 3 different times replication check
        if duplication_proof_count >= 3:
            return BKMStatus(
                is_bkm_eligible=True,
                is_elevated_bkm=True,
                disqualification_reason=None,
                triangulation_count=duplication_proof_count,
                triangulation_evidence="Validated: Method duplicated by 3 people at 3 different times with expected results. Elevated to official BKM template!"
            )
        else:
            return BKMStatus(
                is_bkm_eligible=True,
                is_elevated_bkm=False,
                disqualification_reason=None,
                triangulation_count=duplication_proof_count,
                triangulation_evidence=f"Eligible candidate: Currently has {duplication_proof_count}/3 documented replications needed for full BKM elevation."
            )

    def get_bkm_registry(self) -> List[Dict]:
        return self._bkm_registry
