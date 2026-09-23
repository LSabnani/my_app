import os
import re
import sys
import requests
from pathlib import Path
import chromadb
from chromadb.config import Settings
from config import DATABASE_DIR, SKILLS_DIR, SAMPLE_DOCS_DIR
from services.ollama_service import get_embedding

# Initialize Persistent ChromaDB Client
db_client = chromadb.PersistentClient(path=str(DATABASE_DIR))
skills_collection = db_client.get_or_create_collection(name="skills_db")
docs_collection = db_client.get_or_create_collection(name="documents_db")

def parse_skill_md(skill_path: Path) -> dict:
    """Parses SKILL.md file content into title, description, and raw text."""
    raw_content = skill_path.read_text(encoding="utf-8", errors="ignore")
    
    # Extract name and description from header/metadata
    name_match = re.search(r"#\s*(.+)", raw_content)
    desc_match = re.search(r"## Description\s*\n([^\n#]+)", raw_content)
    
    skill_name = name_match.group(1).strip() if name_match else skill_path.parent.name
    skill_desc = desc_match.group(1).strip() if desc_match else raw_content[:200]
    
    return {
        "id": skill_path.parent.name,
        "name": skill_name,
        "description": skill_desc,
        "content": raw_content,
        "script_path": str(skill_path.parent / "scripts")
    }

def scan_and_update_skills_db():
    """Scans skills/ directory and inserts missing skills into skills_collection."""
    existing_ids = set(skills_collection.get()["ids"])
    new_count = 0
    
    for item in SKILLS_DIR.iterdir():
        if item.is_dir():
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skill_id = item.name
                if skill_id not in existing_ids:
                    info = parse_skill_md(skill_md)
                    vector_text = f"Skill: {info['name']}\nDescription: {info['description']}\n{info['content']}"
                    embedding = get_embedding(vector_text)
                    
                    skills_collection.add(
                        ids=[skill_id],
                        embeddings=[embedding],
                        documents=[info["content"]],
                        metadatas=[{
                            "name": info["name"],
                            "description": info["description"],
                            "folder": skill_id
                        }]
                    )
                    new_count += 1
    return new_count

def query_skills(query: str, threshold: float = 0.2, top_k: int = 5) -> list:
    """Queries skills vector database and returns matches exceeding similarity threshold."""
    if skills_collection.count() == 0:
        scan_and_update_skills_db()
        
    if skills_collection.count() == 0:
        return []
        
    emb = get_embedding(query)
    results = skills_collection.query(
        query_embeddings=[emb],
        n_results=min(top_k, skills_collection.count())
    )
    
    matched = []
    all_candidates = []
    
    if results and results.get("ids") and len(results["ids"]) > 0:
        ids = results["ids"][0]
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[0] * len(ids)])[0]
        
        for i in range(len(ids)):
            dist = distances[i] if i < len(distances) else 0.5
            similarity = max(0.0, min(1.0, 1.0 - dist))
            
            item = {
                "id": ids[i],
                "name": metadatas[i].get("name", ids[i]),
                "description": metadatas[i].get("description", ""),
                "content": docs[i],
                "score": round(float(similarity), 4)
            }
            all_candidates.append(item)
            
            if similarity >= threshold:
                matched.append(item)
                
    # Fallback heuristic: If threshold excluded all skills, check keyword relevance
    if not matched and all_candidates:
        q_lower = query.lower()
        keyword_map = {
            "time-weather-skill": ["time", "weather", "temp", "temperature", "clock", "city", "forecast", "angeles", "hyderabad", "tokyo", "london"],
            "person-information-skill": ["who", "person", "job", "title", "department", "registry", "employee"],
            "stock-market-skill": ["stock", "market", "gainers", "losers", "increase", "decrease", "ticker", "aapl", "nvda"],
            "doc-search-skill": ["document", "rag", "strategy", "report", "marketing", "financial", "overview"]
        }
        for cand in all_candidates:
            s_id = cand["id"]
            for kw in keyword_map.get(s_id, []):
                if kw in q_lower:
                    cand["score"] = max(cand["score"], 0.25)
                    matched.append(cand)
                    break
                    
    matched.sort(key=lambda x: x["score"], reverse=True)
    return matched

def text_chunker(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """Splits text into chunks of specified size and overlap."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += (chunk_size - chunk_overlap)
        if chunk_size <= chunk_overlap:
            break
            
    return chunks

def populate_vector_database(source: str, chunk_size: int = 500, chunk_overlap: int = 50) -> dict:
    """
    Takes a local file/directory path or a web URL, chunks content, and adds to ChromaDB docs_collection.
    Prevents duplicate chunks.
    """
    texts_to_process = []
    
    # URL checking
    if source.startswith("http://") or source.startswith("https://"):
        try:
            res = requests.get(source, timeout=10)
            if res.status_code == 200:
                # Strip simple HTML tags if web URL
                clean_text = re.sub(r'<[^>]+>', ' ', res.text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                texts_to_process.append((source, clean_text))
        except Exception as e:
            return {"error": f"Failed to fetch URL {source}: {str(e)}", "chunks_added": 0}
    else:
        path = Path(source)
        if not path.is_absolute():
            path = (SAMPLE_DOCS_DIR / source).resolve()
            
        if path.is_dir():
            for f in path.glob("**/*"):
                if f.is_file() and f.suffix in [".txt", ".md", ".json", ".csv"]:
                    try:
                        content = f.read_text(encoding="utf-8", errors="ignore")
                        texts_to_process.append((f.name, content))
                    except Exception:
                        pass
        elif path.is_file():
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                texts_to_process.append((path.name, content))
            except Exception as e:
                return {"error": f"Failed to read file {path}: {str(e)}", "chunks_added": 0}
                
    if not texts_to_process:
        return {"error": f"No valid documents found in source: {source}", "chunks_added": 0}
        
    existing_docs = docs_collection.get()
    existing_hashes = set(existing_docs.get("ids", []))
    
    new_ids = []
    new_embs = []
    new_chunks = []
    new_metas = []
    
    for doc_name, text in texts_to_process:
        chunks = text_chunker(text, chunk_size, chunk_overlap)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}_chunk_{idx}_{hash(chunk)}"
            if chunk_id not in existing_hashes:
                emb = get_embedding(chunk)
                new_ids.append(chunk_id)
                new_embs.append(emb)
                new_chunks.append(chunk)
                new_metas.append({
                    "document": doc_name,
                    "chunk_index": idx,
                    "char_count": len(chunk)
                })
                
    if new_ids:
        docs_collection.add(
            ids=new_ids,
            embeddings=new_embs,
            documents=new_chunks,
            metadatas=new_metas
        )
        
    return {
        "status": "success",
        "chunks_added": len(new_ids),
        "documents_processed": len(texts_to_process)
    }

def query_documents(query: str, threshold: float = 0.3, top_k: int = 5) -> dict:
    """Queries document vector database and returns matched chunks grouped by document."""
    if docs_collection.count() == 0:
        # Seed default sample docs if empty
        populate_vector_database(str(SAMPLE_DOCS_DIR))
        
    if docs_collection.count() == 0:
        return {"query": query, "results": [], "grouped": {}}
        
    emb = get_embedding(query)
    results = docs_collection.query(
        query_embeddings=[emb],
        n_results=min(top_k, docs_collection.count())
    )
    
    matched = []
    grouped = {}
    
    if results and results.get("ids") and len(results["ids"]) > 0:
        ids = results["ids"][0]
        chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results.get("distances", [[0] * len(ids)])[0]
        
        for i in range(len(ids)):
            dist = distances[i] if i < len(distances) else 0.5
            similarity = max(0.0, min(1.0, 1.0 - dist))
            
            if similarity >= threshold:
                doc_name = metadatas[i].get("document", "Unknown Document")
                item = {
                    "id": ids[i],
                    "document": doc_name,
                    "chunk_index": metadatas[i].get("chunk_index", 0),
                    "chunk_text": chunks[i],
                    "score": round(float(similarity), 4)
                }
                matched.append(item)
                
                if doc_name not in grouped:
                    grouped[doc_name] = []
                grouped[doc_name].append(item)
                
    matched.sort(key=lambda x: x["score"], reverse=True)
    return {
        "query": query,
        "count": len(matched),
        "results": matched,
        "grouped": grouped
    }

def list_ingested_documents() -> list:
    """Returns aggregated list of ingested documents with chunk count and total characters."""
    if docs_collection.count() == 0:
        return []
        
    data = docs_collection.get()
    metadatas = data.get("metadatas", [])
    
    summary = {}
    for meta in metadatas:
        doc_name = meta.get("document", "Unknown Document")
        chars = meta.get("char_count", 0)
        if doc_name not in summary:
            summary[doc_name] = {"document": doc_name, "chunk_count": 0, "total_characters": 0}
        summary[doc_name]["chunk_count"] += 1
        summary[doc_name]["total_characters"] += chars
        
    return list(summary.values())

def delete_document(doc_name: str) -> bool:
    """Deletes all chunks belonging to a specific document."""
    data = docs_collection.get()
    ids_to_delete = []
    for doc_id, meta in zip(data["ids"], data["metadatas"]):
        if meta.get("document") == doc_name:
            ids_to_delete.append(doc_id)
            
    if ids_to_delete:
        docs_collection.delete(ids=ids_to_delete)
        return True
    return False

def reset_database():
    """Deletes all data in both document and skill vector collections."""
    global docs_collection, skills_collection
    try:
        db_client.delete_collection("documents_db")
        db_client.delete_collection("skills_db")
    except Exception:
        pass
    docs_collection = db_client.get_or_create_collection("documents_db")
    skills_collection = db_client.get_or_create_collection("skills_db")
    return True

def get_ingestion_stats() -> dict:
    """Returns dataset metrics: chunk count, document count, and DB size in MB."""
    doc_count = len(list_ingested_documents())
    chunk_count = docs_collection.count()
    
    total_bytes = 0
    if DATABASE_DIR.exists():
        for root, _, files in os.walk(DATABASE_DIR):
            for f in files:
                total_bytes += os.path.getsize(os.path.join(root, f))
                
    db_size_mb = round(total_bytes / (1024 * 1024), 2)
    return {
        "document_count": doc_count,
        "chunk_count": chunk_count,
        "db_size_mb": db_size_mb
    }
