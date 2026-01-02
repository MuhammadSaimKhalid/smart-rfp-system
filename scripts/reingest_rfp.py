import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.ingestion import ingest_document, DATA_DIR
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def refresh_rfp():
    rfp_path = "drive-download-20251229T152332Z-1-001/AV - Bid Package Audubon Villas.pdf"
    collection_name = "RFP_Context"
    
    print(f"--- Re-ingesting RFP: {rfp_path} ---")
    
    # Force Delete Collection
    db_path = os.path.join(DATA_DIR, "chromadb")
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    
    try:
        print("Clearing existing collection...")
        db = Chroma(persist_directory=db_path, embedding_function=embedding, collection_name=collection_name)
        db.delete_collection()
        print("Collection cleared.")
    except Exception as e:
        print(f"Collection clean error (might not exist): {e}")

    # Re-ingest
    # Use smaller chunks (500) to ensure tables aren't lost in large noise? 
    # Or keep large (1000) for context? 
    # Page 8 was ~900 chars. 1000 should cover it.
    ingest_document(rfp_path, collection_name, chunk_size=1000, chunk_overlap=100)
    print("Re-ingestion complete.")

if __name__ == "__main__":
    refresh_rfp()
