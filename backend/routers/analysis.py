from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from apps.api.services import rfp_service
from services.review.llm_client import complete_json

router = APIRouter(prefix="/analysis", tags=["analysis"])

class Dimension(BaseModel):
    id: str
    name: str
    description: str
    weight: int = 10
    keywords: List[str] = []
    type: str = "dynamic"  # 'general' or 'dynamic'

class AnalysisResponse(BaseModel):
    dimensions: List[Dimension]

SYSTEM_PROMPT = """You are an expert RFP Analyst. Your goal is to extract distinct EVALUATION DIMENSIONS from a Request for Proposal (RFP).

Input:
You will receive the Title, Scope, and Requirements of an RFP.

Output:
A JSON object containing a list of `dimensions`.
Each dimension must have:
- `id`: unique snake_case identifier.
- `name`: Short, professional display name.
- `description`: Brief explanation.
- `weight`: Importance (1-10).
- `keywords`: List of 3-5 specific keywords.
- `type`: EXACTLY one of: "general" OR "dynamic".

Rules:
1. "general" dimensions: You MUST include specific entries for these 6 dimensions:
    - id="experience", name="Experience", type="general", keywords=["track record", "past performance", "years", "qualification"]
    - id="cost", name="Cost", type="general", keywords=["price", "budget", "cost", "fee", "rate"]
    - id="materials_warranty", name="Materials/Warranty", type="general", keywords=["warranty", "guarantee", "quality", "material", "durability"]
    - id="schedule", name="Schedule", type="general", keywords=["timeline", "deadline", "start date", "completion", "turnaround"]
    - id="safety", name="Safety", type="general", keywords=["safety", "osha", "compliance", "regulation", "record"]
    - id="responsiveness", name="Responsiveness", type="general", keywords=["communication", "support", "availability", "service", "response"]

2. "dynamic" dimensions: Extract 3-5 Technical/Scope-specific dimensions.
    - These MUST be marked as `type: "dynamic"`.
    - Do NOT duplicate the general dimensions here.
    - Example: "HVAC Expertise", "Emergency Response", "Safety Compliance".
"""

@router.post("/rfp/{rfp_id}/dimensions", response_model=AnalysisResponse)
async def generate_dimensions(rfp_id: str):
    rfp = rfp_service.get_rfp(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    # Construct prompt
    requirements_text = "\\n".join([f"- {req.text}" for req in rfp.requirements])
    
    prompt = f"""
    RFP Title: {rfp.title}
    
    Scope:
    {rfp.description}
    
    Requirements:
    {requirements_text}
    
    Budget: {rfp.budget}
    Deadline: {rfp.deadline}
    """

    try:
        response = complete_json(SYSTEM_PROMPT, prompt, temperature=0.2)
        return AnalysisResponse(**response)
    except Exception as e:
        print(f"Error generating dimensions: {e}")
        # Fallback if AI fails
        return AnalysisResponse(dimensions=[
            Dimension(id="experience", name="Experience", description="Vendor track record", type="general", keywords=["track record", "history", "years"]),
            Dimension(id="cost", name="Cost", description="Total project cost", type="general", keywords=["price", "cost", "budget"]),
            Dimension(id="materials_warranty", name="Materials/Warranty", description="Quality and guarantees", type="general", keywords=["warranty", "material", "quality"]),
            Dimension(id="schedule", name="Schedule", description="Project timeline", type="general", keywords=["deadline", "schedule", "time"]),
            Dimension(id="safety", name="Safety", description="Safety record and compliance", type="general", keywords=["safety", "osha", "record"]),
            Dimension(id="responsiveness", name="Responsiveness", description="Vendor support and availability", type="general", keywords=["support", "response", "service"])
        ])
# --- Comparison Analysis ---

class ComparisonRequest(BaseModel):
    rfp_id: str
    proposal_ids: List[str]
    dimensions: List[str]

class DimensionScore(BaseModel):
    dimension: str
    score: int
    rationale: str

class ProposalAnalysis(BaseModel):
    proposal_id: str
    scores: List[DimensionScore]

class ComparisonResponse(BaseModel):
    analyses: List[ProposalAnalysis]

COMPARISON_SYSTEM_PROMPT = """You are an expert RFP Analyst. Your goal is to COMPARE proposals against an RFP and score them on specific dimensions.

Input:
- RFP Details (Title, Budget, Deadline, Scope, Requirements).
- List of Proposals (Vendor Name, Price, and detailed structured data).
- List of Dimensions to score (e.g., Cost, Experience, Safety).

Output:
A JSON object with a list of `analyses`.
Each analysis corresponds to a proposal and contains a list of `scores` for each requested dimension.
Each score must have:
- `dimension`: The name of the dimension.
- `score`: Integer 0-100.
    - 90-100: Exceptional / "Best Class" (Matches/exceeds all requirements perfectly).
    - 80-89: Very Good (Strong match, minor gaps).
    - 70-79: Good / Standard (Meets base requirements).
    - 50-69: Fair (Meets some requirements, significant gaps).
    - <50: Poor (Does not meet requirements).
- `rationale`: 1 short sentence explaining exactly WHY this score was given (cite specific data if possible).

Scoring Rules:
- **Cost**: Compare against RFP Budget and other proposals. Lower is better, but extremely low (outlier) might be risky.
- **Schedule**: Compare against RFP Deadline.
- **Experience**: Evaluate specific project history/years.
- Use the provided structured data (Experience bullet points, Safety records, etc.) for evidence.
"""

@router.post("/compare", response_model=ComparisonResponse)
async def compare_proposals(body: ComparisonRequest):
    rfp = rfp_service.get_rfp(body.rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
        
    proposals = []
    for pid in body.proposal_ids:
        p = proposal_service.get_proposal(pid)
        if p:
            proposals.append(p)
            
    if not proposals:
        raise HTTPException(status_code=400, detail="No valid proposals found")

    # Construct Prompt
    # 1. RFP Context
    requirements_text = "\\n".join([f"- {req.text}" for req in rfp.requirements])
    rfp_context = f"""
    RFP TITLE: {rfp.title}
    BUDGET: {rfp.budget or 'TBD'} {rfp.currency}
    DEADLINE: {rfp.deadline or 'TBD'}
    
    SCOPE:
    {rfp.description}
    
    REQUIREMENTS:
    {requirements_text}
    """
    
    # 2. Proposals Data
    proposals_text = ""
    for p in proposals:
        # Format structured data
        experience_txt = "\\n".join(p.experience) if p.experience else "No experience data"
        safety_txt = "\\n".join(p.safety) if p.safety else "No safety data"
        schedule_txt = "\\n".join(p.timeline) if p.timeline else "No schedule data"
        
        # Vendor Bid Form (Summary)
        bid_form_summary = "Bid Form Data Available" if p.proposal_form_data else "No detailed bid form"
        
        proposals_text += f"""
        ---
        PROPOSAL ID: {p.id}
        VENDOR: {p.contractor}
        PRICE: {p.price or 'TBD'} {p.currency}
        START DATE: {p.start_date or 'TBD'}
        SUMMARY: {p.summary}
        
        EXPERIENCE DATA:
        {experience_txt}
        
        SAFETY DATA:
        {safety_txt}
        
        SCHEDULE DATA:
        {schedule_txt}
        
        BID FORM STATUS: {bid_form_summary}
        ---
        """
        
    dimensions_text = ", ".join(body.dimensions)
    
    prompt = f"""
    CONTEXT:
    {rfp_context}
    
    PROPOSALS TO COMPARE:
    {proposals_text}
    
    TASK:
    Score each proposal on the following DIMENSIONS: {dimensions_text}.
    Return the result in the specified JSON format.
    """
    
    print(f"DEBUG: Running AI Comparison for {len(proposals)} proposals on {len(body.dimensions)} dimensions")
    
    try:
        response = complete_json(COMPARISON_SYSTEM_PROMPT, prompt, temperature=0.2)
        return ComparisonResponse(**response)
    except Exception as e:
        print(f"Error in comparison analysis: {e}")
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")
