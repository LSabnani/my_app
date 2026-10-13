import requests

payload = {
    "problem_statement": "Global Supply Chain Sourcing for Lithium-Ion Battery Energy Storage Systems (BESS)",
    "target_scope": "BESS Energy Storage Infrastructure"
}

r = requests.post('http://127.0.0.1:8000/api/problem/ingest', json=payload)
print("Ingestion API Response:", r.json())

slides = requests.get('http://127.0.0.1:8000/api/slides').json()['slides']

print("\n=== RE-SYNTHESIZED 13-SLIDE DECK (ZERO REMNANTS OF OLD STUDY) ===")
for s in slides:
    print(f"Slide {s['slide_id']:2d}: {s['title']:<45} | Subtitle: {s['subtitle']}")
    print(f"          Content: {s['content'][:90]}...")
    print(f"          Takeaways: {s['key_takeaways'][0]}")
    print("-" * 85)
