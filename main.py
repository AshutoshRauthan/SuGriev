from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import json

from fastapi.middleware.cors import CORSMiddleware

# Database imports
from database import (
    create_tables,
    insert_complainant,
    insert_complaint,
    fetch_complaints_by_pincode,
    update_complaint_status,
    get_admin_complaints,
    get_complaint_details,
    get_dashboard_stats
)

# Similarity engine
from similarity_engine import generate_embeddings, is_similar

# Urgency engine
from urgency_engine import get_urgency_data, get_urgency_tag


# FastAPI App

app = FastAPI(
    title="SuGriev – Public Grievance Prioritization System",
    version="1.0"
)

# CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB exists
create_tables()


# Schemas


class ComplaintRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    mobile: str
    gender: str
    district: str
    block: Optional[str] = None
    village_city: Optional[str] = None
    pincode: Optional[str] = None
    address: str

    department: str
    sub_department: str
    attribute: Optional[str] = None
    complaint_district: str
    description: str


class AdminLogin(BaseModel):
    username: str
    password: str


class StatusUpdate(BaseModel):
    status: str



# Helper – Similarity Count


def count_similar_complaints(description, address, pincode, threshold=0.6):
    if not pincode:
        return 0

    existing = fetch_complaints_by_pincode(pincode)
    if not existing:
        return 0

    new_issue_emb, new_address_emb = generate_embeddings(description, address)

    count = 0
    for old_issue, old_address in existing:
        if is_similar(
            new_issue_emb,
            new_address_emb,
            json.loads(old_issue),
            json.loads(old_address),
            threshold
        ):
            count += 1

    return count



# Submit Complaint


@app.post("/api/complaint")
def submit_complaint(data: ComplaintRequest):
    payload = data.dict()

    # Insert complainant
    complainant_id = insert_complainant(payload)

    # Generate embeddings
    issue_emb, address_emb = generate_embeddings(
        payload["description"],
        payload["address"]
    )

    issue_emb_str = json.dumps(issue_emb.tolist())
    address_emb_str = json.dumps(address_emb.tolist())

    # Count similar complaints
    similar_count = count_similar_complaints(
        payload["description"],
        payload["address"],
        payload.get("pincode")
    )

    # Calculate urgency
    urgency_data = get_urgency_data(
        payload["description"],
        payload["address"],
        similar_count,
        datetime.now()
    )

    urgency_score = urgency_data["urgency_score"]
    urgency_level = get_urgency_tag(urgency_score)

    # Insert complaint
    complaint_number = insert_complaint(
        complainant_id=complainant_id,
        complaint_data=payload,
        issue_embedding=issue_emb_str,
        address_embedding=address_emb_str,
        urgency_score=urgency_score,
        urgency_level=urgency_level,
        similar_count=similar_count
    )

    return {
        "message": "Complaint submitted successfully",
        "complaint_number": complaint_number,
        "urgency_score": urgency_score,
        "urgency_level": urgency_level,
        "similar_complaints_detected": similar_count
    }



# Admin Login (Prototype)


@app.post("/api/admin/login")
def admin_login(data: AdminLogin):
    if data.username == "admin" and data.password == "admin":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")



# Admin Dashboard – Complaints


@app.get("/api/admin/complaints")
def admin_dashboard(limit: Optional[int] = None):
    return get_admin_complaints(limit)



# Admin Dashboard – Stats


@app.get("/api/admin/dashboard/stats")
def admin_dashboard_stats():
    return get_dashboard_stats()



# Complaint Details Page


@app.get("/api/admin/complaint/{complaint_number}")
def complaint_details(complaint_number: str):
    data = get_complaint_details(complaint_number)
    if not data:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return data



# Update Complaint Status


@app.put("/api/admin/complaint/{complaint_number}/status")
def update_status(complaint_number: str, data: StatusUpdate):
    update_complaint_status(complaint_number, data.status)
    return {"message": "Status updated successfully"}
