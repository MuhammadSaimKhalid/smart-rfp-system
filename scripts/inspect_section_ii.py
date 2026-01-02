import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.agents.rfp_architect import RFPArchitect
import pypdf

def inspect_section_ii():
    print("--- Inspecting Section II Balcony Restoration ---")
    
    # 1. Get Schema
    architect = RFPArchitect()
    try:
        schema = architect.generate_schema()
        
        # Find Section II
        sec_ii = next((c for c in schema.categories if "Balcony" in c.name or "II " in c.name), None)
        if sec_ii:
            print(f"\nFound Category: {sec_ii.name}")
            print(f"Item Count: {len(sec_ii.items)}")
            if len(sec_ii.items) == 4:
                 print("[PASS] Found exactly 4 items.")
            else:
                 print(f"[FAIL] Found {len(sec_ii.items)} items, expected 4.")
            
            for item in sec_ii.items:
                print(f" - {item.item_id}: {item.description[:50]}...")
        else:
            print("[ERROR] Section II NOT found in schema.")
            
    except Exception as e:
        print(f"Architect Error: {e}")

    # 2. Print Page 7 Text (where Section II resides)
    print("\n--- Raw PDF Content (Page 7 / Index 7) ---")
    reader = pypdf.PdfReader('drive-download-20251229T152332Z-1-001/AV - Bid Package Audubon Villas.pdf')
    print(reader.pages[7].extract_text())

if __name__ == "__main__":
    inspect_section_ii()
