import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def test_painting_only():
    print("--- Testing ONLY Painting Section Extraction ---")
    architect = RFPArchitect()
    
    # 1. Retrieve ONLY Page 8 (Chunk 6 in previous logs, but index might vary)
    # We'll use the query "Painting of Repair Areas"
    rfp_content = architect.get_rfp_context("Painting of Repair Areas V Painting")
    
    print(f"Content Length: {len(rfp_content)}")
    if "Painting of Repair Areas" in rfp_content:
        print("[PASS] 'Painting of Repair Areas' is in the Context.")
    else:
        print("[FAIL] 'Painting of Repair Areas' is NOT in the Context! (This is the root cause)")
        return

    # 2. Prompt for JUST Painting
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data extractor. Extract the 'V Painting of Repair Areas' table as JSON."),
        ("user", "Context:\n{rfp_content}\n\nTask: Extract Section V Painting items.")
    ])
    
    chain = prompt | architect.llm
    
    print("\n--- LLM Output ---")
    result = chain.invoke({"rfp_content": rfp_content})
    print(result.content)

if __name__ == "__main__":
    test_painting_only()
