import sqlite3
from datetime import datetime
import uuid


DB_NAME = "sugriev.db"


def get_connection():
    return sqlite3.connect(DB_NAME)



def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complainants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        mobile TEXT NOT NULL,
        gender TEXT CHECK (gender IN ('male', 'female', 'other')) NOT NULL,
        district TEXT NOT NULL,
        block TEXT,
        village_city TEXT,
        pincode TEXT,
        address TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

  
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_number TEXT UNIQUE NOT NULL,
        complainant_id INTEGER NOT NULL,

        department TEXT NOT NULL,
        sub_department TEXT NOT NULL,
        attribute TEXT,

        complaint_district TEXT NOT NULL,
        description TEXT NOT NULL,

        status TEXT CHECK (status IN ('pending', 'in_progress', 'resolved'))
               DEFAULT 'pending',

        urgency_score INTEGER,
        urgency_level TEXT,
        similar_count INTEGER DEFAULT 0,

        issue_embedding TEXT,
        address_embedding TEXT,

        created_at TEXT NOT NULL,
        updated_at TEXT,

        FOREIGN KEY (complainant_id) REFERENCES complainants(id)
    );
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")



def insert_complainant(data: dict)-> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO complainants (
        first_name, last_name, email, mobile, gender,
        district, block, village_city, pincode, address, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["first_name"],
        data["last_name"],
        data["email"],
        data["mobile"],
        data["gender"],
        data["district"],
        data.get("block"),
        data.get("village_city"),
        data.get("pincode"),
        data["address"],
        datetime.now().isoformat()
    ))

    conn.commit()
    complainant_id = cursor.lastrowid
    conn.close()
    return complainant_id



def generate_complaint_number() -> str:
    return f"SGR-{uuid.uuid4().hex[:8].upper()}"



def insert_complaint(
    complainant_id: int,
    complaint_data: dict,
    issue_embedding: str,
    address_embedding: str,
    urgency_score: int,
    urgency_level: str,
    similar_count: int
) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    complaint_number = generate_complaint_number()

    cursor.execute("""
    INSERT INTO complaints (
        complaint_number, complainant_id,
        department, sub_department, attribute,
        complaint_district, description,
        urgency_score, urgency_level, similar_count,
        issue_embedding, address_embedding,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_number,
        complainant_id,
        complaint_data["department"],
        complaint_data["sub_department"],
        complaint_data.get("attribute"),
        complaint_data["complaint_district"],
        complaint_data["description"],
        urgency_score,
        urgency_level,
        similar_count,
        issue_embedding,
        address_embedding,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
    return complaint_number



def fetch_complaints_by_pincode(pincode: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        c.issue_embedding,
        c.address_embedding
    FROM complaints c
    JOIN complainants u ON c.complainant_id = u.id
    WHERE u.pincode = ?
    """, (pincode,))

    rows = cursor.fetchall()
    conn.close()
    return rows



def update_complaint_status(complaint_number: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE complaints
    SET status = ?, updated_at = ?
    WHERE complaint_number = ?
    """, (
        status,
        datetime.now().isoformat(),
        complaint_number
    ))

    conn.commit()
    conn.close()



def get_admin_complaints(limit=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        complaint_number,
        department,
        complaint_district,
        urgency_level,
        similar_count,
        status,
        created_at
    FROM complaints
    ORDER BY created_at DESC
    """

    if limit:
        query += " LIMIT ?"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "complaint_number": r[0],
            "department": r[1],
            "district": r[2],
            "urgency": r[3],
            "similar_count": r[4],
            "status": r[5],
            "date": r[6][:10]
        }
        for r in rows
    ]


def get_complaint_details(complaint_number: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        c.complaint_number,
        u.first_name, u.last_name, u.email, u.mobile, u.gender,
        u.district, u.block, u.village_city, u.pincode, u.address,
        c.department, c.sub_department, c.attribute,
        c.complaint_district, c.description,
        c.urgency_score, c.urgency_level, c.similar_count,
        c.status,
        c.created_at,
        c.updated_at
    FROM complaints c
    JOIN complainants u ON c.complainant_id = u.id
    WHERE c.complaint_number = ?
    """, (complaint_number,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    keys = [
        "complaint_number",
        "first_name", "last_name", "email", "mobile", "gender",
        "district", "block", "village_city", "pincode", "address",
        "department", "sub_department", "attribute",
        "complaint_district", "description",
        "urgency_score", "urgency_level", "similar_count",
        "status",
        "created_at",
        "updated_at"
    ]

    return dict(zip(keys, row))


def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='in_progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE urgency_level IN ('high', 'critical')
    """)
    high_critical = cursor.fetchone()[0]

    conn.close()

    return {
        "total_complaints": total,
        "pending": pending,
        "in_progress": in_progress,
        "high_critical": high_critical
    }


if __name__ == "__main__":
    create_tables()
