from database import (
    create_tables,
    insert_complainant,
    insert_complaint,
    fetch_complaints_by_pincode,
    update_complaint_status
)

# Step 1: Ensure tables exist
create_tables()

# Step 2: Insert complainant
complainant_data = {
    "first_name": "Arpan",
    "last_name": "Sharma",
    "email": "arpan@example.com",
    "mobile": "7017154898",
    "gender": "male",
    "district": "Dehradun",
    "block": "Raipur",
    "village_city": "Mothrowala",
    "pincode": "248001",
    "address": "Near Govt School"
}

complainant_id = insert_complainant(complainant_data)
print("Inserted complainant ID:", complainant_id)

# Step 3: Insert complaint
complaint_data = {
    "department": "Water Supply",
    "sub_department": "Drinking Water",
    "attribute": "Contamination",
    "complaint_district": "Dehradun",
    "description": "Dirty water supply near school for last 3 days"
}

complaint_number = insert_complaint(
    complainant_id=complainant_id,
    complaint_data=complaint_data,
    embedding="[0.12, 0.34, 0.56]",
    urgency_score=75,
    urgency_level="high"
)

print("Inserted complaint number:", complaint_number)

# Step 4: Fetch complaints by pincode
results = fetch_complaints_by_pincode("248001")
print("Fetched complaints for pincode 248001:")
for r in results:
    print(r)

# Step 5: Update complaint status
update_complaint_status(complaint_number, "in_progress")
print("Complaint status updated successfully.")
