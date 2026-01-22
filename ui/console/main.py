from app.services.student_service import add_student, list_students
from app.services.attendance_service import mark_attendance, get_attendance
from app.services.auth_service import login


def show_menu():
    print("\n--- Student Attendance System ---")
    print("1. Add Student")
    print("2. List Students")
    print("3. Mark Attendance")
    print("4. View Attendance")
    print("5. Exit")
    choice = input("Enter choice: ")
    return choice

def add_student_ui():
    name = input("Enter student name: ")
    roll_no = input("Enter roll number: ")
    class_name = input("Enter class: ")
    section = input("Enter section: ")
    add_student(name, roll_no, class_name, section)

def list_students_ui():
    students = list_students()
    print("\n--- Students ---")
    for s in students:
        print(f"ID: {s[0]}, Name: {s[1]}, Roll: {s[2]}, Class: {s[3]}, Section: {s[4]}")

def mark_attendance_ui():
    list_students_ui()
    student_id = int(input("Enter student ID: "))
    date = input("Enter date (YYYY-MM-DD): ")
    status = input("Enter status (Present/Absent): ")
    mark_attendance(student_id, date, status)

def view_attendance_ui():
    date = input("Enter date to view (YYYY-MM-DD or leave blank for all): ")
    records = get_attendance(date if date else None)
    print("\n--- Attendance Records ---")
    for r in records:
        print(f"ID: {r[0]}, Name: {r[1]}, Roll: {r[2]}, Date: {r[3]}, Status: {r[4]}")

def main():
    # ---- LOGIN SECTION ----
    print("--- Welcome to Student Attendance System ---")
    username = input("Username: ")
    password = input("Password: ")

    success, role = login(username, password)
    if not success:
        print("Invalid credentials! Exiting...")
        return
    print(f"Login successful! Role: {role}")
    # ------------------------

    # Existing menu loop
    while True:
        choice = show_menu()
        if choice == "1":
            add_student_ui()
        elif choice == "2":
            list_students_ui()
        elif choice == "3":
            mark_attendance_ui()
        elif choice == "4":
            view_attendance_ui()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
