import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def test_additions_only():
    print("--- Testing ONLY Additions Section Extraction ---")
    architect = RFPArchitect()
    
    # Retrieve Page 10 (Chunk 10-11 usually)
    rfp_content = architect.get_rfp_context("Additions to Repair Specifications Ad1 Ad2")
    
    if "Additions to Repair Specifications" in rfp_content:
        print("[PASS] 'Additions to Repair Specifications' is in the Context.")
    else:
        print("[FAIL] 'Additions to Repair Specifications' is NOT in the Context!")
        return

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data extractor. Extract the 'Additions to Repair Specifications' table as JSON."),
        ("user", "Context:\n{rfp_content}\n\nTask: Extract 'Additions to Repair Specifications' table.")
    ])
    
    chain = prompt | architect.llm
    
    print("\n--- LLM Output ---")
    result = chain.invoke({"rfp_content": rfp_content})
    print(result.content)

if __name__ == "__main__":
    test_additions_only()
