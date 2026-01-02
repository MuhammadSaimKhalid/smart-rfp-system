import os
import sys
import pandas as pd

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect

def main():
    print("--- Testing RFP Architect Accuracy ---")
    print("Goal: Extract EXACT table structure from RFP PDF (including pre-filled values).")
    
    architect = RFPArchitect()
    try:
        # Generate Schema from the RFP Context (assumed loaded in 'RFP_Context' in ChromaDB)
        schema = architect.generate_schema()
        
        print(f"\nExtracted Title: {schema.title}")
        print("-" * 60)
        
        # Display as a table
        rows = []
        for cat in schema.categories:
            for item in cat.items:
                rows.append({
                    "Category": cat.name, 
                    "ID": item.item_id, 
                    "Description": item.description[:60] + "...", # Truncate for display
                    "Qty": item.quantity, 
                    "Unit": item.unit, 
                    "Pre-Filled Unit Cost": item.pre_filled_unit_cost
                })
        
        df = pd.DataFrame(rows)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
        print(df.to_string())
        
        print("-" * 60)
        
        # Verification Checks
        print("\nVerification Checks:")
        # Check for Section I - Structural
        structural = df[df['Category'].str.contains("Structural", case=False)]
        if not structural.empty:
            print("[PASS] Found 'Structural' Category")
            # Check specific item
            if structural['Description'].str.contains("Wall sheathing", case=False).any():
                print("[PASS] Found 'Wall sheathing repairs'")
            else:
                 print("[FAIL] Missing 'Wall sheathing repairs'")
                 
            # Check pre-filled cost
            prefilled = structural['Pre-Filled Unit Cost'].dropna()
            if not prefilled.empty:
                 print(f"[PASS] Found Pre-Filled Unit Costs: {prefilled.unique()}")
            else:
                 print("[FAIL] Did NOT find Pre-Filled Unit Costs (e.g. $4.10) -- EXPECTED if RFP is blank.")
        else:
            print("[FAIL] Missing 'Structural' Category")
        
        print(f"\nFound Categories: {df['Category'].unique()}")

    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    main()
