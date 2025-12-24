import asyncio
from apps.api.services import proposal_service
from apps.api.schemas.proposal import ProposalCreate

from apps.api.models.db import init_db

# Initialize DB
init_db()

rfp_id = "fa33b7d7-69ff-4fca-97a7-1c2ae3af6e25"

proposals = [
    {
        "rfp_id": rfp_id,
        "contractor": "Apex HVAC Solutions",
        "price": 18000.0,
        "summary": "Comprehensive preventive maintenance plan with quarterly inspections and 4-hour emergency response time.",
        "start_date": "2024-02-01"
    },
    {
        "rfp_id": rfp_id,
        "contractor": "Climate Control Inc.",
        "price": 22500.0,
        "summary": "Premium service agreement including all minor parts and 24/7 priority support. specialized in rooftop units.",
        "start_date": "2024-01-15"
    },
    {
        "rfp_id": rfp_id,
        "contractor": "Reliable Repairs Co.",
        "price": 15000.0,
        "summary": "Basic maintenance package. Filters included. 24h response time for emergencies.",
        "start_date": "2024-02-15"
    }
]

for p_data in proposals:
    try:
        payload = ProposalCreate(**p_data)
        p = proposal_service.create_proposal(payload)
        print(f"Created proposal for {p.contractor} (ID: {p.id})")
    except Exception as e:
        print(f"Error creating proposal for {p_data['contractor']}: {e}")
