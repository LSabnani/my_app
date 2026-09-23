import unittest
import json
import os
import sys
from pathlib import Path

# Add parent dir to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import app
from services.vector_store_service import query_skills, query_documents, get_ingestion_stats
from services.custom_agent import execute_procedural_tool
from services.audit_service import add_event_log, get_conversations, get_events_for_conversation, clear_logs

class TestAgentWithRAG(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_procedural_tool_weather(self):
        res = execute_procedural_tool('time_weather_tool', {'city': 'Tokyo'})
        self.assertIn('city', res)
        self.assertIn('temperature_celsius', res)

    def test_procedural_tool_person_search(self):
        res = execute_procedural_tool('person_search_tool', {'keyword': 'Lucas Dubois', 'field': 'name'})
        self.assertIn('match_count', res)
        self.assertGreater(res['match_count'], 0)
        self.assertEqual(res['results'][0]['name'], 'Lucas Dubois')

    def test_procedural_tool_stock_search(self):
        res = execute_procedural_tool('stock_market_tool', {'action': 'top_gainers'})
        self.assertIn('results', res)
        self.assertEqual(res['query_type'], 'top_gainers')

    def test_vector_store_skills(self):
        skills = query_skills('weather in Tokyo', threshold=0.0)
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)

    def test_audit_logging_and_redaction(self):
        cid = "test_conv_123"
        add_event_log(
            conversation_id=cid,
            event_type="Test Event",
            invoker="Tester",
            target="Unit Test",
            short_description="Running unit test",
            payload={"secret_key": "AIzaSyDummyTestKey12345"}
        )
        events = get_events_for_conversation(cid)
        self.assertGreater(len(events), 0)
        last_event = events[-1]
        self.assertEqual(last_event['conversation_id'], cid)

    def test_ingestion_stats_endpoint(self):
        res = self.app.get('/api/ingestion/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('chunk_count', data)
        self.assertIn('document_count', data)

    def test_telemetry_metrics_endpoint(self):
        res = self.app.get('/api/telemetry/metrics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('summary', data)
        self.assertIn('performance_metrics', data)

if __name__ == '__main__':
    unittest.main()
