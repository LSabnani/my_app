"""Researcher Agent: Baseline primer retrieval and deep dive harvesting across slides, videos, and ScienceDirect peer-reviewed literature."""
from typing import List, Dict, Any
from ..services.wikipedia_service import WikipediaService
from ..services.ppt_harvester import PPTHarvester
from ..services.youtube_harvester import YouTubeHarvester
from ..services.sciencedirect_harvester import ScienceDirectHarvester
from ..models.schemas import BaselinePrimer, CandidateResource


class ResearcherAgent:
    """Orchestrates Stage 1 (Primer) and Stage 2 (PPT, Video, and ScienceDirect Search)."""

    def __init__(self):
        self.wiki_service = WikipediaService()
        self.ppt_harvester = PPTHarvester()
        self.youtube_harvester = YouTubeHarvester()
        self.sciencedirect_harvester = ScienceDirectHarvester()

    async def get_primer(self, topic: str) -> BaselinePrimer:
        """Fetch concise primer definition from Wikipedia / knowledge base."""
        data = await self.wiki_service.get_topic_summary(topic)
        return BaselinePrimer(
            source=data.get("source", "Wikipedia"),
            topic=data.get("topic", topic),
            summary_text=data.get("summary", ""),
            page_url=data.get("page_url"),
            confirmed=False
        )

    async def execute_deep_dive(self, topic: str, intent: str = "") -> List[CandidateResource]:
        """Harvest presentation slide decks, educational videos, and ScienceDirect peer-reviewed literature."""
        ppt_candidates = await self.ppt_harvester.search_decks(topic, intent)
        video_candidates = await self.youtube_harvester.search_videos(topic, intent)
        paper_candidates = await self.sciencedirect_harvester.search_articles(topic, intent)

        # Interleave decks, videos, and ScienceDirect papers
        all_candidates: List[CandidateResource] = []
        max_len = max(len(ppt_candidates), len(video_candidates), len(paper_candidates))
        for i in range(max_len):
            if i < len(ppt_candidates):
                all_candidates.append(ppt_candidates[i])
            if i < len(video_candidates):
                all_candidates.append(video_candidates[i])
            if i < len(paper_candidates):
                all_candidates.append(paper_candidates[i])

        return all_candidates
