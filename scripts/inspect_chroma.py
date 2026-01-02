import os
import sys
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATA_DIR = os.path.join(os.getcwd(), "data")
CHROMA_PATH = os.path.join(DATA_DIR, "chromadb")

def inspect_collections():
    print(f"--- Inspecting ChromaDB at {CHROMA_PATH} ---")
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # We can't easily "list" collections with standard LangChain wrapper, 
    # but we can try to access the specific one we know matches.
    
    coll_name = "Proposal_AV_-__Bid_Analysis___Bids-2-12" # Sanitize match
    print(f"Checking Collection: {coll_name}")
    
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function,
        collection_name=coll_name
    )
    
    # Simple search
    results = db.similarity_search("Total Cost", k=5)
    print(f"Found {len(results)} chunks for 'Total Cost'.")
    for doc in results:
        print(f"\nChunk Page {doc.metadata.get('page')}:")
        print(doc.page_content[:300])

if __name__ == "__main__":
    inspect_collections()
