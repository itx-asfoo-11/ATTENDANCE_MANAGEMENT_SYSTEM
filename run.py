from app.services.student_service import add_student, list_students
from app.services.auth_service import create_user

# Only run once to create admin
create_user("admin", "admin123")


# Add first student
add_student("Asfiya Asim", "101", "10", "A")

# List all students
students = list_students()
print("Students in database:")
for s in students:
    print(s)

from app.services.attendance_service import mark_attendance, get_attendance
from app.services.student_service import list_students

# Get first student id
students = list_students()
student_id = students[0][0]  # id of first student

# Mark attendance
mark_attendance(student_id, "2026-01-17", "Present")

# Fetch attendance
records = get_attendance("2026-01-17")
print("\nAttendance Records:")
for r in records:
    print(r)

from app.services.auth_service import create_user

# Only run once to create admin
#create_user("admin", "admin123")
