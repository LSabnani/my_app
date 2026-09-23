import os
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "registry.csv"

def query_person_registry(keyword: str, field: str = "all") -> dict:
    """
    Searches the 20-sample person registry CSV file by name, city, country, or job title.
    """
    if not DATA_PATH.exists():
        return {"error": "Registry database file not found.", "results": []}
    
    df = pd.read_csv(DATA_PATH)
    keyword_clean = str(keyword).lower().strip()
    
    if field != "all" and field in df.columns:
        matches = df[df[field].astype(str).str.lower().str.contains(keyword_clean, na=False)]
    else:
        # Search across all string columns
        mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword_clean, na=False).any(), axis=1)
        matches = df[mask]
        
    records = matches.to_dict(orient="records")
    return {
        "query_keyword": keyword,
        "filter_field": field,
        "match_count": len(records),
        "results": records
    }

if __name__ == "__main__":
    print(query_person_registry("Lucas"))
