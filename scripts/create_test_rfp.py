import asyncio
from apps.api.services import rfp_service
from apps.api.schemas.rfp import RfpCreate, Requirement
from apps.api.models.db import init_db

# Initialize DB
init_db()

# Data
title = "HVAC Preventive Maintenance & Repairs"
budget = 20000
description = """Scope of Work
The selected contractor will provide preventive maintenance and on-call repair
services for HVAC systems across the following properties:
•3 multifamily buildings
•Total units: 120
•Equipment includes rooftop units and split systems
Services Required:
•Quarterly preventive maintenance inspections
•Filter replacement
•Seasonal system checks (cooling/heating)
•Emergency repair services (24/7 availability)
•Minor parts replacement (major parts excluded unless approved)"""

payload = RfpCreate(
    title=title,
    budget=budget,
    currency="USD",
    description=description,
    requirements=[]
)

# Create
try:
    rfp = rfp_service.create_rfp(payload)
    print(f"SUCCESS: Created RFP with ID: {rfp.id}")
    print(f"Title: {rfp.title}")
    print(f"Budget: {rfp.budget}")
except Exception as e:
    print(f"ERROR: {e}")
