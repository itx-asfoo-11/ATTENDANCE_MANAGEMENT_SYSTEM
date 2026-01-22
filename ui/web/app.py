from flask import Flask, render_template, request, redirect, url_for, session
from app.services.auth_service import login, hash_password, create_user
from app.services.student_service import add_student, list_students
from app.services.attendance_service import mark_attendance, get_attendance
from datetime import date
from app.database.connection import get_connection
from app.services.attendance_service import clean_duplicate_attendance


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Session ke liye zaruri

# ---------------- LOGIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def login_page():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success, role = login(username, password)
        if success:
            session['username'] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials!"
    return render_template("login.html", error=error)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    students = list_students()
    total_students = len(students)

    from app.services.attendance_service import get_attendance
    today = date.today().isoformat()
    records = get_attendance()

    today_records = [r for r in records if r[3] == today]

    present_ids = set(r[0] for r in today_records if r[4].lower() == "present")
    absent_ids  = set(r[0] for r in today_records if r[4].lower() == "absent")

    today_present = len(present_ids)
    today_absent  = len(absent_ids)

    attendance_percentage = round((today_present / total_students * 100) if total_students else 0, 2)

    return render_template(
        "dashboard.html",
        username=username,
        total_students=total_students,
        today_present=today_present,
        today_absent=today_absent,
        attendance_percentage=attendance_percentage
    )

# ---------------- ADD STUDENT ----------------
@app.route("/add_student", methods=["GET", "POST"])
def add_student_page():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    message = ""
    if request.method == "POST":
        try:
            add_student(
                int(request.form["id"]),
                request.form["name"],
                request.form["roll"],
                request.form["class"],
                request.form["section"]
            )
            message = "Student added successfully!"
        except Exception as e:
            message = str(e)

    students = list_students()
    return render_template("add_student.html", message=message, students=students, username=username)

# ---------------- DELETE STUDENT ----------------
@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('add_student_page'))

# ---------------- LIST STUDENTS ----------------
@app.route("/list_students")
def list_students_page():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    students = list_students()
    return render_template("list_students.html", students=students, username=username)

# ---------------- MARK ATTENDANCE ----------------
@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance_page():
    message = None

    if request.method == "POST":
        student_id = request.form.get("student_id")
        status = request.form.get("status")

        # 1. Empty check
        if not student_id:
            message = "❌ Please put student ID"

        # 2. Number check
        elif not student_id.isdigit():
            message = "❌ Student ID must be a number"

        else:
            from app.services.attendance_service import mark_attendance
            result = mark_attendance(int(student_id), status)

            if result == "not_found":
                message = "❌ Please put correct student ID"
            elif result == "already_marked":
                message = "⚠️ Attendance already marked today"
            else:
                message = "✅ Attendance marked successfully"

    return render_template("mark_attendance.html", message=message)


# ---------------- VIEW ATTENDANCE ----------------
@app.route("/view_attendance")
def view_attendance_page():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    records = get_attendance()
    return render_template("view_attendance.html", records=records, username=username)

# ---------------- SEARCH STUDENTS ----------------
@app.route("/search_students", methods=["GET","POST"])
def search_student_page():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    result = []
    if request.method == "POST":
        keyword = request.form["keyword"].lower()
        students = list_students()
        result = [s for s in students if keyword in s[1].lower() or keyword in s[2].lower()]
    return render_template("search_students.html", result=result, username=username)

# ---------------- CHANGE PASSWORD ----------------
@app.route("/change_password", methods=["GET","POST"])
def change_password_page():
    username = session.get('username')
    if not username:
        return redirect(url_for("login_page"))

    message = ""
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE username=?",
                       (hash_password(request.form["new_password"]), username))
        conn.commit()
        conn.close()
        message = "Password updated successfully!"
    return render_template("change_password.html", message=message, username=username)

# ---------------- STUDENT PROFILE ----------------
@app.route("/student/<int:student_id>")
def student_profile(student_id):
    from app.database.connection import get_connection
    conn = get_connection()
    c = conn.cursor()

    # Student info
    c.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = c.fetchone()

    # Unique attendance per date
    c.execute("""
        SELECT date, status 
        FROM attendance 
        WHERE student_id = ?
        GROUP BY date
        ORDER BY date ASC
    """, (student_id,))
    records = c.fetchall()

    # Count present / absent (from UNIQUE records only)
    present_count = 0
    absent_count = 0

    for r in records:
        if r[1].lower() == "present":
            present_count += 1
        else:
            absent_count += 1

    conn.close()

    return render_template(
        "student_profile.html",
        student=student,
        records=records,
        present_count=present_count,
        absent_count=absent_count
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login_page"))
# Clean old duplicate attendance on startup
clean_duplicate_attendance()

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
