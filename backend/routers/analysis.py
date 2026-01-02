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
1. "general" dimensions: You MUST include specific entries for "Cost", "Timeline", and "Experience".
    - id="cost", name="Cost", type="general", keywords=["price", "budget", "cost", "fee"]
    - id="timeline", name="Timeline", type="general", keywords=["schedule", "deadline", "date", "time"]
    - id="experience", name="Experience", type="general", keywords=["track record", "past performance", "years"]
2. "dynamic" dimensions: Extract 3-5 Technical/Scope-specific dimensions.
    - These MUST be marked as `type: "dynamic"`.
    - Do NOT duplicate Cost/Timeline/Experience here.
    - Example: "HVAC Expertise", "Emergency Response", "Safety Compliance".
"""

@router.post("/rfp/{rfp_id}/dimensions", response_model=AnalysisResponse)
async def generate_dimensions(rfp_id: str):
    rfp = rfp_service.get_rfp(rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")

    # Construct prompt
    requirements_text = "\n".join([f"- {req.text}" for req in rfp.requirements])
    
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
            Dimension(id="cost", name="Cost", description="Total project cost", type="general", keywords=["price", "cost", "budget"]),
            Dimension(id="timeline", name="Timeline", description="Project schedule", type="general", keywords=["schedule", "deadline", "date"]),
            Dimension(id="experience", name="Experience", description="Vendor track record", type="general", keywords=["years", "track record", "past performance"])
        ])
