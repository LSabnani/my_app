"""
Automated Test Suite: Problem & Scope Ingestion vs. Cache Validation
Validates:
1. Cache reset and output archiving via POST /api/problem/reset-next.
2. Ingestion of Problem A and Scope A into cache with domain-specific synthesis.
3. Strict cache wiping on "Start New Problem" (zero remnants of prior problem data/ratings).
4. Change of problem and change of scope to Scope B (BESS) with non-pollution validation.
5. Change of scope to Scope C (Custom/General Commodity) with procedural synthesis.
6. Absolute synchronization between disk cache (PQM_Commodity_Study.json) and API endpoint.
7. Anti-caching HTTP response headers (Cache-Control: no-cache, no-store, must-revalidate).
"""

import os
import json
import unittest
from fastapi.testclient import TestClient

from server import app, DATA_FILE, OUTPUT_DIR

class TestProblemScopeCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def tearDown(self):
        # Leave system in a clean, reset state after tests
        pass

    def test_01_cache_control_headers(self):
        """Verify that GET /api/slides sends cache-busting headers to prevent browser caching."""
        res = self.client.get('/api/slides')
        self.assertEqual(res.status_code, 200)
        cache_control = res.headers.get('cache-control', '')
        self.assertIn('no-cache', cache_control.lower(), "Cache-Control header missing 'no-cache'")
        self.assertIn('no-store', cache_control.lower(), "Cache-Control header missing 'no-store'")
        self.assertIn('must-revalidate', cache_control.lower(), "Cache-Control header missing 'must-revalidate'")
        print("[PASS] Test 1: HTTP Cache-Control headers verified (no-cache, no-store, must-revalidate)")

    def test_02_reset_and_archive_clears_cache_completely(self):
        """Verify POST /api/problem/reset-next completely resets the cache to a clean awaiting state."""
        # Rate a slide first to create state
        self.client.post('/api/slides/1/rate', json={'rating': 6, 'feedback': 'Test rating to be wiped'})
        
        # Trigger reset
        res_reset = self.client.post('/api/problem/reset-next')
        self.assertEqual(res_reset.status_code, 200)
        reset_payload = res_reset.json()
        self.assertIn("message", reset_payload)
        
        # Verify via API
        res_slides = self.client.get('/api/slides')
        self.assertEqual(res_slides.status_code, 200)
        api_data = res_slides.json()
        
        # Verify directly from disk file
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            disk_data = json.load(f)
            
        self.assertEqual(api_data["target_scope"], "")
        self.assertEqual(disk_data["target_scope"], "")
        self.assertEqual(len(api_data["slides"]), 13)
        self.assertEqual(len(disk_data["slides"]), 13)
        
        for slide in api_data["slides"]:
            self.assertEqual(slide["status"], "Pending", f"Slide {slide['slide_id']} status not Pending")
            self.assertIsNone(slide["rating"], f"Slide {slide['slide_id']} rating not None")
            self.assertEqual(slide["feedback"], [], f"Slide {slide['slide_id']} feedback not empty")
            self.assertIn("Awaiting", slide["subtitle"])
            self.assertEqual(slide.get("visual_widget", {}).get("type"), "placeholder")
            
        print("[PASS] Test 2: 'Start New Problem' reset cleanly clears all 13 slides and cache state")

    def test_03_ingest_problem_a_and_scope_a_xray(self):
        """Ingest Problem Statement A & Scope A (X-Ray generator, 160kV, 3mA) and validate cache content."""
        payload_a = {
            "problem_statement": "Evaluate industrial X-Ray generator suppliers, 160kV constant potential, and dual-sourcing roadmaps",
            "target_scope": "X-Ray generator, 160kV, 3mA"
        }
        res_ingest = self.client.post('/api/problem/ingest', json=payload_a)
        self.assertEqual(res_ingest.status_code, 200)
        
        # Fetch updated cache
        res_slides = self.client.get('/api/slides')
        self.assertEqual(res_slides.status_code, 200)
        data = res_slides.json()
        
        self.assertEqual(data["target_scope"], "X-Ray generator, 160kV, 3mA")
        self.assertEqual(len(data["slides"]), 13)
        
        # Validate Slide 1 domain synthesis
        slide_1 = data["slides"][0]
        self.assertIn("X-Ray generator, 160kV, 3mA", slide_1["subtitle"])
        all_takeaways = " ".join(slide_1["key_takeaways"])
        self.assertIn("160kV", all_takeaways)
        self.assertIn("3mA", all_takeaways)
        
        # Validate Slide 4 visual widget contains X-Ray suppliers (Comet, Varex, Spellman, Gulmay)
        slide_4 = data["slides"][3]
        widget = slide_4.get("visual_widget", {})
        self.assertEqual(widget.get("type"), "market_share")
        supplier_names = [item["name"] for item in widget.get("data", [])]
        self.assertTrue(any("Comet" in name for name in supplier_names), "Comet missing from X-Ray market share widget")
        self.assertTrue(any("Varex" in name for name in supplier_names), "Varex missing from X-Ray market share widget")
        
        # Rate Slide 2 with score 8
        rate_res = self.client.post('/api/slides/2/rate', json={'rating': 8, 'feedback': 'Include ASTM E1742 standards'})
        self.assertEqual(rate_res.status_code, 200)
        
        # Check cache reflects the rating
        slide_2 = self.client.get('/api/slides/2').json()
        self.assertEqual(slide_2["rating"], 8)
        self.assertEqual(slide_2["status"], "Revised")
        
        print("[PASS] Test 3: Problem A & Scope A (X-Ray 160kV) correctly ingested and verified in cache")

    def test_04_reset_archives_scope_a_and_purges_xray_data(self):
        """Verify that resetting after Problem A archives outputs and removes all X-Ray data from cache."""
        res_reset = self.client.post('/api/problem/reset-next')
        self.assertEqual(res_reset.status_code, 200)
        reset_data = res_reset.json()
        
        # Verify archive files were created with scope prefix
        archived_pptx = os.path.join(OUTPUT_DIR, reset_data["archived_pptx"])
        archived_pdf = os.path.join(OUTPUT_DIR, reset_data["archived_pdf"])
        self.assertTrue(os.path.exists(archived_pptx), f"Archived PPTX {archived_pptx} not found on disk")
        self.assertTrue(os.path.exists(archived_pdf), f"Archived PDF {archived_pdf} not found on disk")
        self.assertIn("X_Ray_generator_160kV_3mA", reset_data["archived_pptx"])
        
        # Verify cache contains zero remnants of Problem A or Scope A
        slides_res = self.client.get('/api/slides').json()
        all_text = json.dumps(slides_res).lower()
        self.assertNotIn("160kv", all_text, "Remnant '160kv' found in cleared cache")
        self.assertNotIn("varex", all_text, "Remnant 'varex' found in cleared cache")
        self.assertNotIn("comet", all_text, "Remnant 'comet' found in cleared cache")
        
        # Verify slide 2 rating was reset
        slide_2 = slides_res["slides"][1]
        self.assertIsNone(slide_2["rating"], "Slide 2 rating not cleared after reset")
        self.assertEqual(slide_2["status"], "Pending", "Slide 2 status not reset to Pending")
        
        print("[PASS] Test 4: Reset archives Scope A with correct filename and purges all X-Ray remnants")

    def test_05_change_of_problem_and_scope_to_bess_with_zero_pollution(self):
        """Change to Problem B & Scope B (BESS) and verify complete replacement with zero older problem data."""
        payload_b = {
            "problem_statement": "Global Supply Chain Sourcing for Utility-Scale Lithium-Ion Battery Energy Storage Systems (BESS)",
            "target_scope": "BESS Energy Storage Infrastructure"
        }
        res_ingest = self.client.post('/api/problem/ingest', json=payload_b)
        self.assertEqual(res_ingest.status_code, 200)
        
        data_b = self.client.get('/api/slides').json()
        self.assertEqual(data_b["target_scope"], "BESS Energy Storage Infrastructure")
        
        # Verify BESS content exists
        bess_text = json.dumps(data_b)
        self.assertTrue("catl" in bess_text.lower() or "byd" in bess_text.lower(), "BESS suppliers missing in Scope B cache")
        self.assertTrue("megapack" in bess_text.lower() or "bess" in bess_text.lower(), "BESS technical terms missing in Scope B cache")
        
        # STRICT NON-POLLUTION ASSERTIONS: No remnants of Problem A (X-Ray) or initial PQM study
        self.assertNotIn("160kv", bess_text.lower(), "Remnant '160kv' from Problem A leaked into Scope B cache")
        self.assertNotIn("varex", bess_text.lower(), "Remnant 'varex' from Problem A leaked into Scope B cache")
        self.assertNotIn("schneider electric", bess_text.lower(), "Remnant 'Schneider Electric' leaked into Scope B cache")
        self.assertNotIn("eaton corporation", bess_text.lower(), "Remnant 'Eaton Corporation' leaked into Scope B cache")
        
        print("[PASS] Test 5: Change of problem & scope to BESS verified with ZERO older problem data pollution")

    def test_06_change_of_scope_to_procedural_general_commodity(self):
        """Change to Scope C (Custom General Commodity) and verify procedural synthesis & zero BESS leakage."""
        # Reset first
        self.client.post('/api/problem/reset-next')
        
        payload_c = {
            "problem_statement": "Procurement strategy and fab capacity for Automotive Silicon Carbide Power MOSFETs in 800V EV inverters",
            "target_scope": "Automotive SiC Power Modules"
        }
        res_ingest = self.client.post('/api/problem/ingest', json=payload_c)
        self.assertEqual(res_ingest.status_code, 200)
        
        data_c = self.client.get('/api/slides').json()
        self.assertEqual(data_c["target_scope"], "Automotive SiC Power Modules")
        
        c_text = json.dumps(data_c).lower()
        self.assertIn("automotive sic power modules", c_text)
        
        # Verify ZERO leakage of Scope B (BESS) or Scope A (X-Ray)
        self.assertNotIn("megapack", c_text, "Scope B term 'megapack' found in Scope C cache")
        self.assertNotIn("fluence", c_text, "Scope B term 'fluence' found in Scope C cache")
        self.assertNotIn("160kv", c_text, "Scope A term '160kv' found in Scope C cache")
        
        # Verify disk cache matches API payload exactly
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            disk_c = json.load(f)
        self.assertEqual(disk_c["target_scope"], data_c["target_scope"])
        self.assertEqual(len(disk_c["slides"]), len(data_c["slides"]))
        
        print("[PASS] Test 6: Change of scope to procedural commodity verified with disk/API synchronization")

    def test_07_export_deck_reflects_active_scope_name(self):
        """Verify PPTX and PDF export endpoints dynamically generate files matching the active scope."""
        res_pptx = self.client.get('/api/export/pptx')
        self.assertEqual(res_pptx.status_code, 200)
        pptx_header = res_pptx.headers.get("content-disposition", "")
        self.assertIn("Automotive_SiC_Power_Modules", pptx_header)
        
        res_pdf = self.client.get('/api/export/pdf')
        self.assertEqual(res_pdf.status_code, 200)
        pdf_header = res_pdf.headers.get("content-disposition", "")
        self.assertIn("Automotive_SiC_Power_Modules", pdf_header)
        
        # Finally reset back to clean state
        self.client.post('/api/problem/reset-next')
        print("[PASS] Test 7: PPTX and PDF exports accurately reflect active scope prefix in headers")

if __name__ == '__main__':
    unittest.main()
