import sqlite3
from datetime import date
from app.database.connection import get_connection

def mark_attendance(student_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today().isoformat()

    # Check student exists
    cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return "not_found"

    # Check already marked today
    cursor.execute("""
        SELECT id FROM attendance 
        WHERE student_id = ? AND date = ?
    """, (student_id, today))

    already = cursor.fetchone()

    if already:
        conn.close()
        return "already_marked"

    # Insert attendance
    cursor.execute("""
        INSERT INTO attendance (student_id, date, status)
        VALUES (?, ?, ?)
    """, (student_id, today, status))

    conn.commit()
    conn.close()

    return "success"

def get_attendance():
    from app.database.connection import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attendance.student_id,
               students.name,
               students.roll_no,
               attendance.date,
               attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """)

    records = cursor.fetchall()
    conn.close()
    return records
def clean_duplicate_attendance():
    conn = get_connection()
    cursor = conn.cursor()

    # Keep only latest record per student per date
    cursor.execute("""
        DELETE FROM attendance
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM attendance
            GROUP BY student_id, date
        )
    """)

    conn.commit()
    conn.close()
