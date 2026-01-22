from app.database.connection import get_connection

def add_student(student_id, name, roll, class_name, section):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (id, name, roll_no, class, section)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, name, roll, class_name, section))

    conn.commit()
    conn.close()


def list_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def attendance_percentage(student_id):
    from app.database.connection import get_connection
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM attendance WHERE student_id=?", (student_id,))
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'", (student_id,))
    present = c.fetchone()[0]

    conn.close()
    if total==0:
        return 0
    return int((present/total)*100)
