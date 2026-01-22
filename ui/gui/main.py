import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from app.services.auth_service import login
from app.services.student_service import add_student, list_students
from app.services.attendance_service import mark_attendance, get_attendance
from app.database.connection import get_connection

# ---------------------- LOGIN WINDOW ----------------------
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Student Attendance - Login")

        tk.Label(master, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(master, text="Password:").grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=0, column=1)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(master, text="Login", command=self.login_user).grid(row=2, column=0, columnspan=2, pady=10)

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, role = login(username, password)
        if success:
            messagebox.showinfo("Login Success", f"Welcome {username} ({role})")
            self.master.destroy()
            root = tk.Tk()
            DashboardWindow(root)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

# ---------------------- DASHBOARD WINDOW ----------------------
class DashboardWindow:
    def __init__(self, master):
        self.master = master
        master.title("Student Attendance - Dashboard")

        tk.Button(master, text="Add Student", width=20, command=self.add_student_ui).pack(pady=10)
        tk.Button(master, text="List Students", width=20, command=self.list_students_ui).pack(pady=10)
        tk.Button(master, text="Mark Attendance", width=20, command=self.mark_attendance_ui).pack(pady=10)
        tk.Button(master, text="View Attendance", width=20, command=self.view_attendance_ui).pack(pady=10)
        tk.Button(master, text="Export Attendance CSV", width=20, command=self.export_attendance).pack(pady=10)
        tk.Button(master, text="Search Students", width=20, command=self.search_student_ui).pack(pady=10)
        tk.Button(master, text="Change Password", width=20, command=self.change_password_ui).pack(pady=10)
        tk.Button(master, text="Exit", width=20, command=master.quit).pack(pady=10)

    # ---------------------- STUDENT FUNCTIONS ----------------------
    def add_student_ui(self):
        win = tk.Toplevel(self.master)
        win.title("Add Student")

        tk.Label(win, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(win, text="Roll No:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(win, text="Class:").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(win, text="Section:").grid(row=3, column=0, padx=5, pady=5)

        name_entry = tk.Entry(win)
        roll_entry = tk.Entry(win)
        class_entry = tk.Entry(win)
        section_entry = tk.Entry(win)

        name_entry.grid(row=0, column=1)
        roll_entry.grid(row=1, column=1)
        class_entry.grid(row=2, column=1)
        section_entry.grid(row=3, column=1)

        def submit():
            add_student(name_entry.get(), roll_entry.get(), class_entry.get(), section_entry.get())
            messagebox.showinfo("Success", f"Student {name_entry.get()} added!")
            win.destroy()

        tk.Button(win, text="Add", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

    def list_students_ui(self):
        win = tk.Toplevel(self.master)
        win.title("List Students")
        students = list_students()
        for s in students:
            tk.Label(win, text=f"ID:{s[0]}, Name:{s[1]}, Roll:{s[2]}, Class:{s[3]}, Section:{s[4]}").pack()

    # ---------------------- ATTENDANCE FUNCTIONS ----------------------
    def mark_attendance_ui(self):
        win = tk.Toplevel(self.master)
        win.title("Mark Attendance")
        students = list_students()

        tk.Label(win, text="Select Student ID:").pack()
        student_ids = [str(s[0]) for s in students]
        student_var = tk.StringVar(win)
        student_var.set(student_ids[0])
        tk.OptionMenu(win, student_var, *student_ids).pack()

        tk.Label(win, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(win)
        date_entry.pack()

        tk.Label(win, text="Status (Present/Absent):").pack()
        status_entry = tk.Entry(win)
        status_entry.pack()

        def submit():
            mark_attendance(int(student_var.get()), date_entry.get(), status_entry.get())
            messagebox.showinfo("Success", f"Attendance marked!")
            win.destroy()

        tk.Button(win, text="Submit", command=submit).pack(pady=5)

    def view_attendance_ui(self):
        win = tk.Toplevel(self.master)
        win.title("Attendance Records")
        tk.Label(win, text="Leave date blank to view all").pack()
        date_entry = tk.Entry(win)
        date_entry.pack()

        def fetch():
            records = get_attendance(date_entry.get() or None)
            for widget in win.pack_slaves():
                if isinstance(widget, tk.Label) and widget != date_entry:
                    widget.destroy()
            for r in records:
                tk.Label(win, text=f"ID:{r[0]}, Name:{r[1]}, Roll:{r[2]}, Date:{r[3]}, Status:{r[4]}").pack()

        tk.Button(win, text="View", command=fetch).pack(pady=5)

    # ---------------------- EXTRA FEATURES ----------------------
    def export_attendance(self):
        records = get_attendance(None)
        if not records:
            messagebox.showinfo("Info", "No attendance records found!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Attendance Report"
        )
        if not file_path:
            return
        
        with open(file_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Roll No", "Date", "Status"])
            for r in records:
                writer.writerow(r)
        
        messagebox.showinfo("Success", f"Attendance exported to {file_path}")

    def search_student_ui(self):
        win = tk.Toplevel(self.master)
        win.title("Search Students")

        tk.Label(win, text="Enter Name or Roll No:").pack()
        search_entry = tk.Entry(win)
        search_entry.pack()

        def search():
            keyword = search_entry.get().lower()
            students = list_students()
            results = [s for s in students if keyword in s[1].lower() or keyword in s[2].lower()]

            for widget in win.pack_slaves():
                if isinstance(widget, tk.Label) and widget != search_entry:
                    widget.destroy()

            if results:
                for s in results:
                    tk.Label(win, text=f"ID:{s[0]}, Name:{s[1]}, Roll:{s[2]}, Class:{s[3]}, Section:{s[4]}").pack()
            else:
                tk.Label(win, text="No students found").pack()

        tk.Button(win, text="Search", command=search).pack(pady=5)

    def change_password_ui(self):
        from app.services.auth_service import hash_password
        win = tk.Toplevel(self.master)
        win.title("Change Password")

        tk.Label(win, text="Username:").pack()
        username_entry = tk.Entry(win)
        username_entry.pack()
        tk.Label(win, text="New Password:").pack()
        password_entry = tk.Entry(win, show="*")
        password_entry.pack()

        def submit():
            username = username_entry.get()
            new_pass = password_entry.get()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hash_password(new_pass), username))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Password updated for {username}")
            win.destroy()

        tk.Button(win, text="Change Password", command=submit).pack(pady=5)

# ---------------------- START GUI ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
