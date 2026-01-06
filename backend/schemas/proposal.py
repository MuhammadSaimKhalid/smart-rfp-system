from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field


class ProposalBase(BaseModel):
    rfp_id: str
    contractor: str = Field(..., example="Acme Builders")
    contractor_email: Optional[str] = Field(None, example="bid-team@example.com")
    price: Optional[float] = Field(None, example=45000.0)
    currency: str = Field(default="USD")
    start_date: Optional[date] = None
    summary: Optional[str] = None
    
    # Enhanced extraction fields (JSON arrays of bullet points)
    experience: Optional[List[str]] = Field(default_factory=list, description="Experience bullet points")
    scope_understanding: Optional[List[str]] = Field(default_factory=list, description="Scope understanding bullet points")
    materials: Optional[List[str]] = Field(default_factory=list, description="Materials/equipment bullet points")
    timeline: Optional[List[str]] = Field(default_factory=list, description="Timeline bullet points")
    warranty: Optional[List[str]] = Field(default_factory=list, description="Warranty terms bullet points")
    safety: Optional[List[str]] = Field(default_factory=list, description="Safety practices bullet points")
    cost_breakdown: Optional[List[str]] = Field(default_factory=list, description="Cost breakdown bullet points")
    termination_term: Optional[List[str]] = Field(default_factory=list, description="Termination terms bullet points")
    references: Optional[List[str]] = Field(default_factory=list, description="References bullet points")
    
    # Legacy fields (kept for backward compatibility)
    methodology: Optional[str] = Field(None, description="Proposed methodology or approach")
    warranties: Optional[str] = Field(None, description="Warranty terms (legacy)")
    timeline_details: Optional[str] = Field(None, description="Detailed timeline breakdown (legacy)")

    extracted_text: Optional[str] = None
    dimensions: Optional[dict] = Field(default_factory=dict, description="Dynamic comparison dimensions")
    proposal_form_data: Optional[list] = Field(default_factory=list, description="Vendor's filled proposal form values")


class ProposalCreate(ProposalBase):
    pass


class Proposal(ProposalBase):
    id: str
    status: str = Field(default="submitted")
    created_at: datetime

    class Config:
        from_attributes = True

