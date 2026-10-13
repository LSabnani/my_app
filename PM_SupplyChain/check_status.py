import json

with open('PQM_Commodity_Study.json', 'r') as f:
    data = json.load(f)

print("=== SLIDE APPROVAL STATUS ===")
for s in data['slides']:
    status = s.get('status', 'Pending')
    rating = s.get('rating', 'Unrated')
    print(f"Slide {s['slide_id']:2d}: {s['title']:<45} | Status: {status:<10} | Rating: {rating}")
