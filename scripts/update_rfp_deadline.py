from datetime import date
from sqlmodel import select
from apps.api.models.db import get_session, init_db
from apps.api.models.entities import RfpModel

init_db()

rfp_id = "fa33b7d7-69ff-4fca-97a7-1c2ae3af6e25"

with get_session() as session:
    rfp = session.get(RfpModel, rfp_id)
    if rfp:
        rfp.deadline = date(2025, 12, 31)
        session.add(rfp)
        session.commit()
        print(f"Updated RFP {rfp.title} deadline to {rfp.deadline}")
    else:
        print("RFP not found")
