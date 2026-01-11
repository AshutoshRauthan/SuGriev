from database import (
    create_tables,
    insert_complainant,
    insert_complaint,
    fetch_complaints_by_pincode,
    update_complaint_status
)


create_tables()

#these are exampler values only
complainant_data = {
    "first_name": "Arpan",
    "last_name": "Sharma",
    "email": "arpan@example.com",
    "mobile": "--mobile number ---- ",
    "gender": "male",
    "district": "Dehradun",
    "block": "---loca---",
    "village_city": "---locat---",
    "pincode": "--pin---",
    "address": "--near School--"
}

complainant_id = insert_complainant(complainant_data)
print("Inserted complainant ID:", complainant_id)


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

results = fetch_complaints_by_pincode("248001")
print("Fetched complaints for pincode 248001:")
for r in results:
    print(r)


update_complaint_status(complaint_number, "in_progress")
print("Complaint status updated successfully.")
