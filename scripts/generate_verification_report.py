import os
import sys
import pandas as pd
import asyncio

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from backend.src.agents.bid_estimator import BidEstimator

def main():
    print("--- Starting Verification Report Generation ---")
    
    # 1. Define Paths
    rfp_path = "drive-download-20251229T152332Z-1-001/AV - Bid Package Audubon Villas.pdf"
    proposal_path = "ilovepdf_split-range/AV -  Bid Analysis & Bids-2-12.pdf"
    output_excel = "Verification_Report.xlsx"

    if not os.path.exists(rfp_path):
        print(f"Error: RFP not found at {rfp_path}")
        return
    if not os.path.exists(proposal_path):
        print(f"Error: Proposal not found at {proposal_path}")
        return

    # 2. Architect: Extract Schema
    print("\n--- Step 1: Architect (Schema Extraction) ---")
    architect = RFPArchitect()
    try:
        # Ensure RFP is ingested (or re-ingested depending on implementation, 
        # usually Architect assumes it's already in 'RFP_Context' from ingestion.py run)
        # We assume ingestion.py was run for the RFP.
        schema = architect.generate_schema()
        print("Schema Extracted successfully.")
    except Exception as e:
        print(f"Architect failed: {e}")
        return

    # 3. Estimator: Extract Values
    print("\n--- Step 2: Estimator (Value Extraction) ---")
    estimator = BidEstimator()
    filled_proposal = estimator.process_proposal(proposal_path, schema)

    if not filled_proposal:
        print("Estimator failed to extract values.")
        return
    
    print(f"Extraction Complete for: {filled_proposal.vendor_name}")
    print(f"Grand Total: {filled_proposal.grand_total}")

    # 4. Generate Excel
    print("\n--- Step 3: Generating Excel ---")
    rows = []
    
    # Flatten the filled proposal
    for category in filled_proposal.categories:
        for item in category.items:
            rows.append({
                "Vendor": filled_proposal.vendor_name,
                "Category": category.name,
                "Item ID": item.item_id,
                "Description": item.description,
                "Quantity": item.quantity,
                "Unit": item.unit,
                "Unit Cost": item.unit_cost,
                "Total Cost": item.total_cost,
                "Grand Total Detected": filled_proposal.grand_total
            })
            
    if not rows:
        # If rows are empty (maybe lumpsum only?), add a summary row
        rows.append({
            "Vendor": filled_proposal.vendor_name,
            "Grand Total Detected": filled_proposal.grand_total,
            "Note": "No line items extracted (Lump Sum)"
        })

    df = pd.DataFrame(rows)
    df.to_excel(output_excel, index=False)
    print(f"Report saved to: {os.path.abspath(output_excel)}")

if __name__ == "__main__":
    main()
