import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from backend.src.agents.bid_estimator import BidEstimator

def debug_estimator():
    print("--- Debugging Estimator Extraction ---")
    
    # 1. Get Schema
    architect = RFPArchitect()
    # To save time, we might just define a mock schema or use the real one.
    # Real one ensures we are matching the real IDs.
    schema = architect.generate_schema()
    
    # 2. Extract from Dueall (Bids 2-12)
    pdf_path = "ilovepdf_split-range/AV -  Bid Analysis & Bids-2-12.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    estimator = BidEstimator()
    filled_proposal = estimator.process_proposal(pdf_path, schema)
    
    if filled_proposal:
        print("\n--- Extracted Data Sample (First Category) ---")
        if filled_proposal.categories:
            cat = filled_proposal.categories[0]
            print(f"Category: {cat.name}")
            for item in cat.items[:5]: # First 5 items
                print(f"  ID: {item.item_id}")
                print(f"    Desc: {item.description[:50]}...")
                print(f"    Vendor Qty: {item.quantity} | Unit: {item.unit}")
                print(f"    Unit Cost: {item.unit_cost}")
                print(f"    Total Cost: {item.total_cost}")
                print("-" * 20)
                
    else:
        print("Extraction returned None.")

if __name__ == "__main__":
    debug_estimator()
