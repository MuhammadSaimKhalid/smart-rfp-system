from datetime import date
from sqlmodel import select
from apps.api.models.db import get_session, init_db
from apps.api.models.entities import RfpModel, ProposalModel
from apps.api.services import proposal_service
from apps.api.schemas.proposal import ProposalCreate

def setup():
    init_db()
    
    target_id = "d317e0a5-b7c3-40c0-a10b-7952588c6432"
    
    with get_session() as session:
        # 1. Clean/Create RFP
        existing_rfp = session.get(RfpModel, target_id)
        if existing_rfp:
            print(f"Updating existing RFP {target_id}...")
            rfp = existing_rfp
        else:
            print(f"Creating new RFP {target_id}...")
            rfp = RfpModel(id=target_id, title="Temp", status="open")
            session.add(rfp)
            session.commit()
            session.refresh(rfp)

        rfp.title = "HVAC Preventive Maintenance & Repairs"
        rfp.deadline = date(2025, 12, 31)
        rfp.status = "open"
        rfp.requirements = [
             {"id": "r1", "text": "Contract duration must be strictly one year."},
             {"id": "r2", "text": "Vendor must provide 24/7 emergency response service."},
             {"id": "r3", "text": "Includes quarterly preventive maintenance visits."},
             {"id": "r4", "text": "Technicians must have 5+ years of experience."}
        ]
        session.add(rfp)
        
        # 2. Clear proposals
        statement = select(ProposalModel).where(ProposalModel.rfp_id == target_id)
        props = session.exec(statement).all()
        for p in props:
            session.delete(p)
        
        session.commit()
        print("RFP Updated and old proposals cleaned.")

    # 3. Seed Proposals
    proposals_data = [
        {
            "rfp_id": target_id,
            "contractor": "Apex HVAC Solutions",
            "price": 18000.0,
            "summary": "We offer a 1-year contract with 4-hour emergency response.",
            "status": "submitted"
        },
        {
            "rfp_id": target_id,
            "contractor": "Climate Control Inc.",
            "price": 22500.0,
            "summary": "Premium annual contract. 24/7 support guaranteed. 10 years experience.",
            "status": "submitted"
        },
        {
            "rfp_id": target_id,
            "contractor": "Reliable Repairs Co.",
            "price": 15000.0,
            "summary": "Standard maintenance. Emergency response next business day.",
            "status": "submitted"
        }
    ]

    print("Seeding new proposals...")
    for p_data in proposals_data:
        try:
            payload = ProposalCreate(**p_data)
            proposal_service.create_proposal(payload)
            print(f"Created proposal: {p_data['contractor']}")
        except Exception as e:
            print(f"Failed to create {p_data['contractor']}: {e}")

if __name__ == "__main__":
    setup()
