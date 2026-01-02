import os
import shutil
import logging
from fastapi import UploadFile
from backend.src.agents.rfp_architect import RFPArchitect
from backend.src.agents.bid_estimator import BidEstimator
from backend.src.agents.ingestion import ingest_document

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths relative to the backend (assumes running from project root)
DATA_DIR = os.path.join(os.getcwd(), "data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

class AnalysisAgent:
    def __init__(self):
        self.architect = RFPArchitect()
        self.estimator = BidEstimator()

    async def extract_table(self, file_path: str):
        """
        Main entry point for the API.
        This handles the 'Upload Proposal' workflow (Hybrid Type 1).
        
        Logic:
        1. Access the already saved Proposal PDF (via file_path).
        2. Ingest it into ChromaDB (Proposal Collection).
        3. Use the Architect to get the RFP Schema (Cached or Regenerated).
        4. Use the Estimator to extract values for this Proposal.
        5. Return the structured data.
        """
        try:
            logger.info(f"Processing Proposal from: {file_path}")
            
            # 1. Generate Schema (The Target Structure)
            # In a real app, successful Schema generation should be done ONCE per RFP and saved.
            # Here we generate it on the fly from the Vector DB context.
            logger.info("Generating Schema...")
            schema = self.architect.generate_schema()
            
            # 2. Extract Values
            # The Estimator handles ingestion internally now (with force reset)
            logger.info("Extracting Values...")
            filled_proposal = self.estimator.process_proposal(file_path, schema)
            
            if filled_proposal:
                logger.info(f"Extraction Successful. Grand Total: {filled_proposal.grand_total}")
                # Transform to Frontend Format
                # The frontend expects a flat list or specific structure. 
                # We'll return the 'categories' list which contains items.
                return {
                    "vendor_name": filled_proposal.vendor_name,
                    "grand_total": filled_proposal.grand_total,
                    "categories": [c.dict() for c in filled_proposal.categories]
                }
            else:
                 logger.error("Extraction failed: returned None")
                 return {"error": "Extraction failed"}

        except Exception as e:
            logger.error(f"Analysis Failed: {e}")
            return {"error": str(e)}
