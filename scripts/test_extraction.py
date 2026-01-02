import os
import sys
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.api.services.analysis_agent import AnalysisAgent
from PyPDF2 import PdfReader

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        # Limit to 10 pages
        full_text = ""
        for i, page in enumerate(reader.pages):
            if i >= 10: break
            text = page.extract_text()
            full_text += f"\n\n--- Page {i+1} ---\n{text}"
        return full_text
    except Exception as e:
        return f"Error: {e}"

def test_rfp_extraction(pdf_path):
    print(f"--- Processing RFP: {pdf_path} ---")
    
    # 1. Extract Text
    # For better results with tables, pdfplumber is better, but let's try the existing one first 
    # or just use the agent's internal logic if we updated it.
    # Actually, let's use the one we just wrote in analyze_pdf (which uses PyPDF2)
    # The Agent expects a string (rfp_text).
    
    rfp_text = extract_text(pdf_path)
    
    # 2. Agent Extraction
    agent = AnalysisAgent()
    try:
        print("Invoking Agent to extract schema...")
        result = agent.extract_rfp_structure(rfp_text)
        print("\n--- Extracted Schema ---")
        print(result.model_dump_json(indent=2))
        return result
    except Exception as e:
        print(f"Extraction failed: {e}")

if __name__ == "__main__":
    # Check for API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in env. Agent calls will fail if not set.")
    
    pdf_path = "drive-download-20251229T152332Z-1-001/AV - Bid Package Audubon Villas.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
    test_rfp_extraction(pdf_path)
