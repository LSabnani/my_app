"""Greeter Agent: Intake and contextual inquiry."""
from typing import Dict, Any


class GreeterAgent:
    """Manages conversational intake and purpose elicitation."""

    def initial_greeting(self) -> Dict[str, Any]:
        return {
            "message": "Welcome to Explainer. What is the problem or area of focus that you want the explainer to search and get?",
            "prompt_stage": "PROBLEM_INTAKE",
            "suggested_topics": [
                "Microservices Distributed Tracing",
                "Transformer Attention Mechanisms in LLMs",
                "Kubernetes Zero-Downtime Rolling Upgrades",
                "OAuth2 PKCE Authentication Flow"
            ]
        }

    def process_intake(self, problem: str, intent: str = "", target_application: str = "") -> Dict[str, Any]:
        """Analyzes problem statement and ensures user context is captured."""
        clean_problem = problem.strip()
        needs_context = not intent.strip() and not target_application.strip()

        return {
            "problem": clean_problem,
            "intent": intent.strip() or "Comprehensive conceptual mastery and practical overview",
            "target_application": target_application.strip() or "Technical decision making and reference",
            "needs_context": needs_context,
            "followup_question": "Why do you want to learn about this, and what will you use that understanding for?" if needs_context else None
        }
