import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import ProposalSchema, Category, LineItem
from backend.services.report_generator import ReportGenerator

def test_fully_dynamic_matrix():
    print("--- Testing Fully Dynamic Generic Matrix ---")
    
    # 1. Simulate AI Discovery of NON-STANDARD Headers
    # Scenario: A Service RFP (Task, Hours, Rate) instead of Construction (Item, Qty, Unit)
    mock_headers = ["Task ID", "Scope of Work", "Estimated Hours", "Hourly Rate", "Total Amount"]
    
    # 2. Mock Schema
    schema = ProposalSchema(
        title="Service Proposal",
        rfp_headers=mock_headers,
        categories=[
            Category(name="Phase 1: Analysis", items=[
                LineItem(item_id="1.1", description="Requirement Gathering", quantity="20", unit="Hrs", extra_fields={}),
                LineItem(item_id="1.2", description="System Design", quantity="40", unit="Hrs", extra_fields={})
            ])
        ]
    )
    
    # 3. Mock Vendor Data (Mapping to these dynamic headers)
    # The Generic Engine converts "Estimated Hours" -> "estimated_hours" key
    vendor_data = {
        "Consulting Inc": {
            "1.1": {"estimated_hours": 20, "hourly_rate": 150, "total_amount": 3000},
            "1.2": {"estimated_hours": 40, "hourly_rate": 150, "total_amount": 6000}
        },
        "Cheap Devs LLC": {
            # Intentionally missing one item to test robustness
            "1.1": {"estimated_hours": 15, "hourly_rate": 50, "total_amount": 750}
        }
    }
    
    vendors = ["Consulting Inc", "Cheap Devs LLC"]
    
    # 4. Generate
    gen = ReportGenerator(output_dir=".")
    output = gen.generate_comparison_matrix(schema, vendors, vendor_data)
    
    print(f"\n[SUCCESS] Generated: {output}")
    print(f"Verify that columns are: {mock_headers}")
    print("Specifically, look for 'Estimated Hours' and 'Hourly Rate' columns for CACH vendor.")

if __name__ == "__main__":
    test_fully_dynamic_matrix()
