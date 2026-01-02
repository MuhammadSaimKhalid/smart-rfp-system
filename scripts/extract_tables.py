import os
import sys
import pandas as pd
from PyPDF2 import PdfReader
from apps.api.services.analysis_agent import AnalysisAgent

def extract_text(pdf_path, max_pages=None):
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for i, page in enumerate(reader.pages):
            if max_pages and i >= max_pages: break
            text = page.extract_text()
            full_text += f"\n\n--- Page {i+1} ---\n{text}"
        return full_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY must be set.")
        return

    base_dir = "drive-download-20251229T152332Z-1-001"
    rfp_filename = "AV - Bid Package Audubon Villas.pdf"
    rfp_path = os.path.join(base_dir, rfp_filename)

    agent = AnalysisAgent()

    # 1. Extract RFP Schema
    print(f"--- Extracting Schema from {rfp_filename} ---")
    rfp_text = extract_text(rfp_path, max_pages=15) # Schema is likely in first 15 pages
    rfp_schema = agent.extract_rfp_structure(rfp_text)
    
    print("\n--- Schema Extracted ---")
    print(f"Found {len(rfp_schema.categories)} categories.")

    # 2. Identify Proposals
    proposals = [
        f for f in os.listdir(base_dir) 
        if f.endswith(".pdf") and f != rfp_filename and "Analysis" not in f and "Materials" not in f
    ]
    
    print(f"\n--- Found {len(proposals)} Proposals ---")
    results = []

    # 3. Extract Values for each Proposal
    for prop_file in proposals:
        prop_path = os.path.join(base_dir, prop_file)
        print(f"Processing {prop_file}...")
        
        prop_text = extract_text(prop_path) # Read whole proposal
        
        # Run Agent
        filled_schema = agent.extract_proposal_values(prop_text, rfp_schema)
        
        # Flatten for DataFrame
        for cat in filled_schema.categories:
            for item in cat.items:
                row = {
                    "Vendor": prop_file,
                    "Category": cat.name,
                    "Item ID": item.item_id,
                    "Description": item.description,
                    "Quantity": item.quantity,
                    "Unit": item.unit,
                    "Unit Cost": item.unit_cost,
                    "Total Cost": item.total_cost
                }
                results.append(row)

    # 4. Generate Report
    if results:
        df = pd.DataFrame(results)
        output_path = "Proposal_Comparison_Report.xlsx"
        df.to_excel(output_path, index=False)
        print(f"\n--- Report Generated: {output_path} ---")
        print(df.head())
    else:
        print("No results extracted.")

if __name__ == "__main__":
    main()
