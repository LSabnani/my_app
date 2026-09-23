import sys
from pathlib import Path

# Add project base to path to import vector store service
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

def query_document_store(query: str, top_k: int = 5, doc_threshold: float = 0.3) -> dict:
    """
    Wrapper tool to search ChromaDB document collection.
    """
    try:
        from services.vector_store_service import query_documents
        return query_documents(query=query, top_k=top_k, threshold=doc_threshold)
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "results": []
        }

if __name__ == "__main__":
    print(query_document_store("marketing strategy"))
