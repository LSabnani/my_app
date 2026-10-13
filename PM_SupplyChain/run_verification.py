import requests

r = requests.post('http://127.0.0.1:8000/api/slides/verify-all')
print("HTTP Status:", r.status_code)
data = r.json()

print("\n=== CRITIC AGENT LIVE HTTP REFERENCE VERIFICATION SUMMARY ===")
for s in data['summary']:
    print(f"Slide {s['slide_id']:2d}: {s['title']:<45} | Critic Status: {s['status']:<8}")
    print(f"          Notes: {s['notes']}")
