import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from backend.services.report_generator import ReportGenerator

def test_filled_matrix():
    print("--- Testing Filled Report Generation (Mock Data) ---")
    
    # 1. Get Real Schema
    architect = RFPArchitect()
    try:
        schema = architect.generate_schema() # Real Extraction from RFP
    except Exception as e:
        print(f"Architect Error: {e}")
        return

    # 2. Mock Data (Simulating what Estimator Agent would return)
    # We will fill just the first few items to prove the concept
    
    # Try to find some real item IDs from the schema to match
    first_item_id = schema.categories[0].items[0].item_id # e.g. "1" in Structural
    
    vendor_data = {
        "Dueall Construction": {
            first_item_id: {"unit_price": 50.00, "quantity": 100, "unit": "LF"},
            "Ad1": {"unit_price": 4.10, "quantity": 1000, "unit": "SF"} # Example addition
        },
        "Empire Works": {
             first_item_id: {"unit_price": 65.00, "quantity": 100, "unit": "LF"},
             "Ad1": {"unit_price": 5.50, "quantity": 1200, "unit": "SF"}
        }
    }
    
    vendors = list(vendor_data.keys())
    
    # 3. Generate Report
    report_gen = ReportGenerator(output_dir=".")
    output_path = report_gen.generate_comparison_matrix(schema, vendors, vendor_data)
    
    print(f"\n[SUCCESS] Generated: {output_path}")
    print("Open this file. You should see 'Dueall' and 'Empire' columns FILLED with the mock values ($50, $65).")

if __name__ == "__main__":
    test_filled_matrix()
