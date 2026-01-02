import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
from backend.services.report_generator import ReportGenerator

def test_dynamic_matrix():
    print("--- Testing Dynamic Report Generator ---")
    
    # 1. Get Schema
    architect = RFPArchitect()
    try:
        # Mocking schema generation to save time/cost or use cached?
        # For meaningful test, let's run it.
        schema = architect.generate_schema()
    except Exception as e:
        print(f"Architect Error: {e}")
        return

    # 2. Simulate AI defining vendors
    vendors = ["Dueall Construction", "Empire Works", "ABC Solutions"]
    
    # 3. Call the Tool
    report_gen = ReportGenerator(output_dir=".")
    output_path = report_gen.generate_comparison_matrix(schema, vendors)
    
    print(f"\n[SUCCESS] Generated: {output_path}")
    print("Verify this file has 3 Vendor Blocks (Red, Green, Purple).")

if __name__ == "__main__":
    test_dynamic_matrix()
