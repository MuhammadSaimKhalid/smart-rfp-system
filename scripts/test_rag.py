import os
import sys
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATA_DIR = os.path.join(os.getcwd(), "data")
CHROMA_PATH = os.path.join(DATA_DIR, "chromadb")

def test_retrieval(query: str):
    print(f"--- Querying: {query} ---")
    
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function,
        collection_name="RFP_Context"
    )
    
    # Retrieve top 3 chunks
    results = db.similarity_search_with_score(query, k=3)
    
    if not results:
        print("No results found.")
        return

    for i, (doc, score) in enumerate(results):
        print(f"\nResult {i+1} (Score: {score:.4f}):")
        print(f"Content Preview: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")

if __name__ == "__main__":
    test_retrieval("Submission Date")
