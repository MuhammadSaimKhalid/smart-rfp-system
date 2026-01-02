import os
import sys
import pypdf

def search_rfp_for_price():
    rfp_path = "drive-download-20251229T152332Z-1-001/AV - Bid Package Audubon Villas.pdf"
    target_value = "4.10"
    
    print(f"--- Searching {rfp_path} for '{target_value}' ---")
    
    try:
        reader = pypdf.PdfReader(rfp_path)
        found = False
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if target_value in text:
                print(f"[FOUND] Page {i+1} contains '{target_value}'")
                print(f"Context: ...{text[text.find(target_value)-50 : text.find(target_value)+50]}...")
                found = True
        
        if not found:
            print(f"[NOT FOUND] The string '{target_value}' does not appear in the text layer of this PDF.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_rfp_for_price()
