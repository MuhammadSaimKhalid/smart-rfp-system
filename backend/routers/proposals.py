from pathlib import Path
from datetime import date

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from apps.api.config.settings import settings
from apps.api.schemas.proposal import Proposal, ProposalCreate
from apps.api.schemas.review import ReviewResult
from apps.api.services import notification_service, proposal_service, rfp_service
from services.ingest.extractor import extract_text
from services.ingest.parser import extract_emails
from services.ingest.ai_extractor import extract_details_with_ai

router = APIRouter(tags=["proposals"])


def parse_price_to_float(value) -> float | None:
    """
    Safely parse a price value to float.
    Handles: '$1,295,648.70', '1295648.70', 1295648.70, None
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove $, commas, whitespace
        cleaned = value.replace('$', '').replace(',', '').strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None



@router.get("/proposals", response_model=list[Proposal])
def list_proposals(rfp_id: str | None = None):
    return proposal_service.list_proposals(rfp_id=rfp_id)


@router.post("/proposals", response_model=Proposal, status_code=201)
def create_proposal(payload: ProposalCreate):
    if not rfp_service.get_rfp(payload.rfp_id):
        raise HTTPException(status_code=404, detail="RFP not found")
    return proposal_service.create_proposal(payload)


@router.post("/proposals/upload", response_model=Proposal, status_code=201)
async def upload_proposal(
    rfp_id: str = Form(...),
    contractor: str = Form(...),
    price: float | None = Form(None),
    currency: str = Form("USD"),
    start_date: str | None = Form(None),
    summary: str | None = Form(None),
    contractor_email: str | None = Form(None),
    file: UploadFile = File(...),
):
    """Create a proposal plus upload a PDF for AI to read."""
    if not rfp_service.get_rfp(rfp_id):
        raise HTTPException(status_code=404, detail="RFP not found")

    payload = ProposalCreate(
        rfp_id=rfp_id,
        contractor=contractor,
        contractor_email=contractor_email,
        price=price,
        currency=currency,
        start_date=start_date,
        summary=summary,
    )
    proposal = proposal_service.create_proposal(payload)

    # Save file to storage and extract text
    base = Path(settings.storage_path) / "proposals" / rfp_id
    base.mkdir(parents=True, exist_ok=True)
    pdf_path = base / f"{proposal.id}.pdf"
    with pdf_path.open("wb") as f:
        f.write(await file.read())

    text = extract_text(str(pdf_path))

    # --- AI Data Extraction ---
    # ALWAYS extract all fields for comparison purposes
    # AI will extract: contractor_name, price, summary, experience, methodology, warranties, timeline_details
    extracted_data = extract_details_with_ai(text)
    
    # --- New Multi-Agent High-Precision Extraction ---
    from backend.services.analysis_agent import AnalysisAgent
    agent = AnalysisAgent()
    try:
        table_data = await agent.extract_table(str(pdf_path))
        if "error" not in table_data:
            # Override/Merge with high-precision data
            extracted_data["price"] = table_data.get("grand_total")
            extracted_data["contractor_name"] = table_data.get("vendor_name")
            # Store the detailed categories as 'dimensions' which the DB model supports
            extracted_data["dimensions"] = table_data.get("categories")
            print(f"DEBUG: Integrated Agent Data: Price={extracted_data['price']}")
    except Exception as e:
        print(f"Agent Extraction Failed: {e}")
    
    # --- NEW: Extract Vendor's Filled Proposal Form using SAME FormStructureAnalyzer ---
    # Treat the vendor proposal just like an RFP - use the same architect to extract form data
    vendor_form_data = []
    vendor_form_schema = None
    try:
        from backend.src.agents.form_structure_analyzer import FormStructureAnalyzer
        from backend.src.agents.ingestion import ingest_document
        
        print(f"--- Extracting vendor form data using FormStructureAnalyzer (same as RFP) ---")
        
        # Ingest vendor proposal PDF into a unique collection
        vendor_collection = f"Vendor_Proposal_{proposal.id}"
        ingest_document(str(pdf_path), collection_name=vendor_collection, reset=True)
        
        # Use the SAME FormStructureAnalyzer that we use for RFPs
        analyzer = FormStructureAnalyzer()
        
        # Get context from vendor proposal (same method as RFP)
        proposal_context = analyzer.get_proposal_form_context(collection_name=vendor_collection, k=20)
        
        if proposal_context:
            # Discover structure (same as RFP)
            structure = analyzer.discover_form_structure(proposal_context)
            
            # Extract rows (same as RFP)
            rows = analyzer.extract_form_rows(proposal_context, structure)
            
            # Convert to dict format for storage
            vendor_form_data = [row.model_dump() for row in rows]
            vendor_form_schema = structure.model_dump()
            
            print(f"✓ Extracted {len(vendor_form_data)} vendor form rows using FormStructureAnalyzer")
            print(f"  Vendor columns: {structure.vendor_columns}")
            
            # DEBUG: Print first 3 rows to see what was extracted
            print(f"  DEBUG - First 3 extracted rows:")
            for i, row in enumerate(vendor_form_data[:3]):
                print(f"    Row {i+1}: item_id={row.get('item_id')}, qty={row.get('quantity')}, unit={row.get('unit')}, unit_cost={row.get('unit_cost')}, total={row.get('total')}")
        else:
            print("⚠ No proposal form context found in vendor PDF")
            
    except Exception as form_err:
        print(f"⚠ Vendor form extraction failed (non-fatal): {form_err}")
        import traceback
        traceback.print_exc()
    
    extracted_data["proposal_form_data"] = vendor_form_data
    extracted_data["proposal_form_schema"] = vendor_form_schema

    
    # Populate missing fields if extraction was successful
    if not contractor or contractor.lower() in ("n/a", "not captured", "unknown", "ai will extract this"):
         if val := extracted_data.get("contractor_name"):
             contractor = val
    
    if price is None:
         if val := extracted_data.get("price"):
             price = parse_price_to_float(val)
             
    if currency == "USD":  # Default value, check if AI found something different
         if val := extracted_data.get("currency"):
             currency = val
             
    if not start_date:
         if val := extracted_data.get("start_date"):
             start_date = val

    if not summary:
         if val := extracted_data.get("summary"):
             summary = val
    
    # ALWAYS extract these fields for comparison (even if user provided some basic fields)
    experience = extracted_data.get("experience")
    methodology = extracted_data.get("methodology")
    warranties = extracted_data.get("warranties")
    timeline_details = extracted_data.get("timeline_details")

    # Extract an email address from the PDF if one was not provided.
    if not contractor_email:
        emails = extract_emails(text)
        if emails:
            contractor_email = emails[0]
    
    proposal_service.update_extracted_text(proposal.id, text)
    
    # Update fields that might have been populated by AI or extraction
    # We always update if we have new values to ensure persistence
    refreshed = proposal_service.get_proposal(proposal.id)
    if refreshed:
        from apps.api.models.db import get_session
        from apps.api.models.entities import ProposalModel
        with get_session() as session:
            db_p = session.get(ProposalModel, proposal.id)
            if db_p:
                if contractor_email:
                    db_p.contractor_email = contractor_email
                
                # Update other fields if they were extracted and differ
                if contractor and contractor != db_p.contractor:
                    db_p.contractor = contractor
                if price is not None and price != db_p.price:
                    parsed_price = parse_price_to_float(price)
                    if parsed_price is not None:
                        db_p.price = parsed_price
                if currency and currency != db_p.currency:
                    db_p.currency = currency
                if start_date and start_date != db_p.start_date:
                    if isinstance(start_date, str):
                        try:
                            db_p.start_date = date.fromisoformat(start_date)
                        except ValueError:
                            pass
                    else:
                         db_p.start_date = start_date
                if summary and summary != db_p.summary:
                    db_p.summary = summary
                
                # Update new extended fields
                if experience:
                    db_p.experience = experience
                if methodology:
                    db_p.methodology = methodology
                if warranties:
                    db_p.warranties = warranties
                if timeline_details:
                    db_p.timeline_details = timeline_details

                # Save dynamic dimensions
                if dimensions := extracted_data.get("dimensions"):
                    if isinstance(dimensions, dict):
                        db_p.dimensions = dimensions
                
                # Save vendor proposal form data (NEW)
                if proposal_form_data := extracted_data.get("proposal_form_data"):
                    if isinstance(proposal_form_data, list):
                        db_p.proposal_form_data = proposal_form_data
                    
                session.add(db_p)
                session.commit()

    # Return refreshed proposal with extracted_text set
    return proposal_service.get_proposal(proposal.id)


@router.get("/proposals/{proposal_id}", response_model=Proposal)
def get_proposal(proposal_id: str):
    proposal = proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/proposals/{proposal_id}/approve", response_model=Proposal)
def approve_proposal(proposal_id: str):
    proposal = proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    rfp = rfp_service.get_rfp(proposal.rfp_id)
    updated = proposal_service.set_status(proposal_id, "Accepted")
    if rfp and updated:
        notification_service.send_approval_email(
            rfp_title=rfp.title,
            contractor_email=updated.contractor_email or "",
            contractor_name=updated.contractor,
        )
    return updated


@router.post("/proposals/{proposal_id}/reject", response_model=Proposal)
def reject_proposal(proposal_id: str):
    proposal = proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    rfp = rfp_service.get_rfp(proposal.rfp_id)
    updated = proposal_service.set_status(proposal_id, "Rejected")
    if rfp and updated:
        # Use latest AI review to drive the explanation email.
        from apps.api.services import review_service

        review_dict = review_service.get_review_summary(proposal_id)
        if review_dict:
            review = ReviewResult.model_validate(review_dict)
            notification_service.send_rejection_email(
                rfp_title=rfp.title,
                contractor_email=updated.contractor_email or "",
                contractor_name=updated.contractor,
                review=review,
            )
    return updated


@router.get("/proposals/{rfp_id}/matrix")
def get_proposal_matrix(rfp_id: str):
    """
    Returns a unified comparison matrix of the RFP line items 
    vs the filled values from each vendor proposal.
    
    DYNAMIC: Columns are determined by rfp.proposal_form_schema.vendor_columns
    """

    rfp = rfp_service.get_rfp(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
        
    proposals = proposal_service.list_proposals(rfp_id=rfp_id)
    
    # Get dynamic columns from RFP schema
    rfp_schema = rfp.proposal_form_schema or {}
    vendor_columns = rfp_schema.get('vendor_columns', ['Unit Cost', 'Total'])  # Fallback
    fixed_columns = rfp_schema.get('fixed_columns', ['Item', 'Description'])
    
    # Helper function to parse numeric values
    def parse_number(value):
        if not value or str(value).upper() in ('TBD', 'N/A', '-', ''):
            return None
        try:
            # Remove $, commas, and whitespace
            cleaned = str(value).replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    # Find the "Total" column for grand total calculation
    total_column = next((c for c in vendor_columns if 'total' in c.lower()), None)
    
    # Track grand totals per proposal
    vendor_grand_totals = {p.id: 0.0 for p in proposals}
    
    rfp_rows = rfp.proposal_form_rows or []
    matrix_rows = []
    
    for r_row in rfp_rows:
        item_id = r_row.get('item_id')
        
        row_data = {
            "section": r_row.get('section'),
            "item_id": item_id,
            "description": r_row.get('description'),
            "quantity": r_row.get('quantity'),
            "unit": r_row.get('unit'),
            "vendor_values": {}
        }
        
        for p in proposals:
            # Find matching row in p.proposal_form_data
            p_data = p.proposal_form_data or []
            
            # Match by item_id (primary)
            match = next((x for x in p_data if str(x.get('item_id')).strip() == str(item_id).strip()), None)
            
            # Get values dict (new dynamic format) or construct from legacy fields
            if match:
                values = match.get('values', {})
                
                # Fallback for legacy format (unit_cost, total fields)
                if not values:
                    values = {}
                    for col in vendor_columns:
                        col_key = col.lower().replace(' ', '_').replace('%', 'percent')
                        if col_key in match:
                            values[col] = match[col_key]
            else:
                values = {}
            
            # Add to grand total if we have a Total column
            if total_column and total_column in values:
                total_num = parse_number(values.get(total_column))
                if total_num is not None:
                    vendor_grand_totals[p.id] += total_num
            
            row_data["vendor_values"][p.id] = values
        
        matrix_rows.append(row_data)
    
    # Add Grand Total row
    grand_total_row = {
        "section": None,
        "item_id": "GRAND_TOTAL",
        "description": "GRAND TOTAL",
        "quantity": "",
        "unit": "",
        "vendor_values": {}
    }
    
    for p in proposals:
        grand_total_values = {}
        if total_column:
            grand_total_values[total_column] = f"${vendor_grand_totals[p.id]:,.2f}"
        grand_total_row["vendor_values"][p.id] = grand_total_values
    
    matrix_rows.append(grand_total_row)
        
    return {
        "rfp_title": rfp.title,
        "vendor_columns": vendor_columns,  # Dynamic columns for frontend
        "fixed_columns": fixed_columns,
        "proposals": [{"id": p.id, "vendor": p.contractor, "status": p.status} for p in proposals],
        "rows": matrix_rows
    }


