import pandas as pd
import os

report_path = "/home/linux/Projects/RFP System/Verification_Report.xlsx"
print(f"--- Inspecting {report_path} ---")

try:
    df = pd.read_excel(report_path)
    
    # Check General Conditions
    gc_df = df[df['Category'].str.contains('General', case=False, na=False)]
    print("\n--- General Conditions Values ---")
    print(gc_df[['Description', 'Quantity', 'Unit', 'Unit Cost', 'Total Cost']].head())

except Exception as e:
    print(f"Error reading Excel: {e}")
