import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import mysql.connector
from mysql.connector import Error

class DatabaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Education Database Management System")
        
        self.connection = self.create_connection()
        if self.connection:
            self.create_use_database()
            self.create_tables()
        else:
            messagebox.showerror("Error", "Failed to connect to the database. Please check your connection settings.")
            self.root.destroy()
            return
        
        # Left frame for displaying results
        self.left_frame = tk.Frame(root, width=400, height=600, padx=20, pady=20)
        self.left_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Right frame for main menu
        self.right_frame = tk.Frame(root, padx=20, pady=20)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)
        
        # Text widget to display results
        self.result_text = tk.Text(self.left_frame, wrap=tk.WORD, width=60, height=20)
        self.result_text.pack()

        # Buttons for main menu
        self.create_buttons()

    
    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',  # Replace with your MySQL password
                database='education'  # Assuming 'education' database already exists
            )
            if connection.is_connected():
                print("Connection to MySQL server successful")
                return connection
        except Error as e:
            print(f"Error: '{e}'")
            return None

    def create_use_database(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS education")
            cursor.execute("USE education")
            print("Database 'education' created and selected successfully.")
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: '{err}'")

    def create_tables(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS `instructors` (
                    `instructor_id` INTEGER PRIMARY KEY AUTO_INCREMENT, 
                    `instructor_name` VARCHAR(255) NOT NULL,
                    `email` VARCHAR(255),
                    `phone` VARCHAR(255),
                    `bio` TEXT,
                    `is_deleted` ENUM('yes', 'no') DEFAULT 'no'
                )""",
            """CREATE TABLE IF NOT EXISTS `course` (
                    `course_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `course_name` VARCHAR(255) NOT NULL,
                    `description` TEXT,
                    `credit_hours` INTEGER,
                    `instructor_id` INTEGER,
                    `is_deleted` ENUM('yes', 'no') DEFAULT 'no',
                    FOREIGN KEY (`instructor_id`) REFERENCES `instructors` (`instructor_id`) ON DELETE CASCADE
                )""",
            """CREATE TABLE IF NOT EXISTS `students` (
                    `student_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `student_name` VARCHAR(255) NOT NULL,
                    `email` VARCHAR(255),
                    `phone` VARCHAR(255),
                    `is_deleted` ENUM('yes', 'no') DEFAULT 'no'
                )""",
            """CREATE TABLE IF NOT EXISTS `enrolments` (
                    `enrolment_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `course_id` INTEGER,
                    `student_id` INTEGER,
                    `enrolment_date` DATE,
                    `completion_status` ENUM('enrolled', 'completed'),
                    `is_deleted` ENUM('yes', 'no') DEFAULT 'no',
                    FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE,
                    FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE
                )""",
            """CREATE TABLE IF NOT EXISTS `assessments` (
                    `assessment_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
                    `course_id` INTEGER,
                    `assessment_name` VARCHAR(255) NOT NULL,
                    `max_score` INTEGER,
                    `given_by` INTEGER,
                    `given_to` INTEGER,
                    `is_deleted` ENUM('yes', 'no') DEFAULT 'no',
                    FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE,
                    FOREIGN KEY (`given_by`) REFERENCES `instructors` (`instructor_id`) ON DELETE CASCADE,
                    FOREIGN KEY (`given_to`) REFERENCES `students` (`student_id`) ON DELETE CASCADE
                )"""
        ]
        try:
            cursor = self.connection.cursor()
            for query in queries:
                cursor.execute(query)
            self.connection.commit()
            print("Tables created successfully.")
        except mysql.connector.Error as err:
            print(f"Error: '{err}'")

    def create_buttons(self):
        buttons = [
            ("Insert Instructor", self.insert_instructor),
            ("Insert Course", self.insert_course),
            ("Insert Student", self.insert_student),
            ("Insert Enrollment", self.insert_enrollment),
            ("Insert Assessment", self.insert_assessment),
            ("Delete Instructor", self.delete_instructor),
            ("Delete Course", self.delete_course),
            ("Delete Student", self.delete_student),
            ("Delete Assessment", self.delete_assessment),
            ("View Records", self.view_records),
            ("View Deleted Records", self.view_deleted_records),
            ("Search Records", self.search_records_button),
            ("Sort Instructors by Name", lambda: self.sort_instructors("instructor_name")),
            ("Sort Instructors by Email", lambda: self.sort_instructors("email")),
            ("Sort Courses by Name", lambda: self.sort_courses("course_name")),
            # Add more sort buttons for other tables as needed
            ("Exit Program", self.exit_program)
        ]

        row = 1
        for text, command in buttons:
            tk.Button(self.right_frame, text=text, width=30, command=command).grid(row=row, column=0, pady=5)
            row += 1

    def insert_instructor(self):
        self.show_insert_window("Insert Instructor", ["Name", "Email", "Phone", "Bio"], self.insert_instructor_db)

    def insert_course(self):
        instructors = self.fetch_instructors()
        if not instructors:
            messagebox.showerror("Error", "No instructors found. Please insert an instructor first.")
            return
        
        labels = ["Name", "Description", "Credit Hours", "Instructor"]
        self.show_insert_window("Insert Course", labels, self.insert_course_db, dropdown_values=instructors)

    def insert_student(self):
        self.show_insert_window("Insert Student", ["Name", "Email", "Phone"], self.insert_student_db)

    def insert_enrollment(self):
        courses = self.fetch_courses()
        students = self.fetch_students()
        if not courses or not students:
            messagebox.showerror("Error", "No courses or students found. Please insert courses and students first.")
            return
        
        labels = ["Course", "Student", "Enrollment Date (YYYY-MM-DD)", "Completion Status"]
        self.show_insert_window("Insert Enrollment", labels, self.insert_enrollment_db, dropdown_values=courses + students)

    def insert_assessment(self):
        courses = self.fetch_courses()
        instructors = self.fetch_instructors()
        students = self.fetch_students()
        if not courses or not instructors or not students:
            messagebox.showerror("Error", "No courses, instructors, or students found. Please insert all necessary data first.")
            return
        
        labels = ["Course", "Assessment Name", "Max Score", "Given By (Instructor)", "Given To (Student)"]
        self.show_insert_window("Insert Assessment", labels, self.insert_assessment_db, dropdown_values=courses + instructors + students)

    def delete_instructor(self):
        instructors = self.fetch_instructors()
        if not instructors:
            messagebox.showerror("Error", "No instructors found.")
            return
        
        self.show_delete_window("Delete Instructor", "Instructor", instructors, self.delete_instructor_db)

    def delete_course(self):
        courses = self.fetch_courses()
        if not courses:
            messagebox.showerror("Error", "No courses found.")
            return
        
        self.show_delete_window("Delete Course", "Course", courses, self.delete_course_db)

    def delete_student(self):
        students = self.fetch_students()
        if not students:
            messagebox.showerror("Error", "No students found.")
            return
        
        self.show_delete_window("Delete Student", "Student", students, self.delete_student_db)

    def delete_assessment(self):
        assessments = self.fetch_assessments()
        if not assessments:
            messagebox.showerror("Error", "No assessments found.")
            return
        
        self.show_delete_window("Delete Assessment", "Assessment", assessments, self.delete_assessment_db)

    def view_records(self):
        self.show_view_records_menu("View Records", ["View Instructors", "View Courses", "View Students", "View Enrollments", "View Assessments"], self.view_records_db)

    def view_deleted_records(self):
        self.show_view_records_menu("View Deleted Records", ["View Deleted Instructors", "View Deleted Courses", "View Deleted Students", "View Deleted Assessments"], self.view_deleted_records_db)

    def exit_program(self):
        self.root.destroy()

    def show_insert_window(self, title, labels, callback, dropdown_values=None):
        window = tk.Toplevel(self.root)
        window.title(title)
        
        entries = []
        for i, label_text in enumerate(labels):
            label = tk.Label(window, text=label_text)
            label.grid(row=i, column=0, padx=10, pady=5)
            
            if dropdown_values and i == len(labels) - 1:
                entry = ttk.Combobox(window, values=dropdown_values)
            else:
                entry = tk.Entry(window)
                
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)
        
        submit_button = tk.Button(window, text="Submit", command=lambda: self.submit_insert(entries, callback, window))
        submit_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def show_delete_window(self, title, label_text, options, callback):
        window = tk.Toplevel(self.root)
        window.title(title)
        
        label = tk.Label(window, text=f"Select {label_text} to delete:")
        label.grid(row=0, column=0, padx=10, pady=5)
        
        delete_var = tk.StringVar(window)
        delete_var.set(options[0])  # default value
        
        dropdown = tk.OptionMenu(window, delete_var, *options)
        dropdown.grid(row=0, column=1, padx=10, pady=5)
        
        submit_button = tk.Button(window, text="Submit", command=lambda: callback(delete_var.get()))
        submit_button.grid(row=1, column=0, columnspan=2, pady=10)


    def show_view_records_menu(self, title, options, callback):
        window = tk.Toplevel(self.root)
        window.title(title)
        
        for i, option in enumerate(options):
            button = tk.Button(window, text=option, width=30, command=lambda opt=option: callback(opt))
            button.grid(row=i, column=0, pady=5)

    def submit_insert(self, entries, callback, window):
        values = [entry.get() for entry in entries]
        if all(values):
            callback(values)
            window.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def insert_instructor_db(self, values):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO instructors (instructor_name, email, phone, bio) VALUES (%s, %s, %s, %s)",
                           (values[0], values[1], values[2], values[3]))
            self.connection.commit()
            messagebox.showinfo("Success", "Instructor inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error inserting instructor: {err}")

    def insert_course_db(self, values):
        try:
            cursor = self.connection.cursor()
            # Fetch instructor_id based on instructor_name
            cursor.execute("SELECT instructor_id FROM instructors WHERE instructor_name = %s", (values[3],))
            instructor_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO course (course_name, description, credit_hours, instructor_id) VALUES (%s, %s, %s, %s)",
                           (values[0], values[1], values[2], instructor_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Course inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error inserting course: {err}")

    def insert_student_db(self, values):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO students (student_name, email, phone) VALUES (%s, %s, %s)",
                           (values[0], values[1], values[2]))
            self.connection.commit()
            messagebox.showinfo("Success", "Student inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error inserting student: {err}")

    def insert_enrollment_db(self, values):
        try:
            cursor = self.connection.cursor()
            # Fetch course_id based on course_name
            cursor.execute("SELECT course_id FROM course WHERE course_name = %s", (values[0],))
            course_id = cursor.fetchone()[0]
            
            # Fetch student_id based on student_name
            cursor.execute("SELECT student_id FROM students WHERE student_name = %s", (values[1],))
            student_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO enrolments (course_id, student_id, enrolment_date, completion_status) VALUES (%s, %s, %s, %s)",
                           (course_id, student_id, values[2], values[3]))
            self.connection.commit()
            messagebox.showinfo("Success", "Enrollment inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error inserting enrollment: {err}")

    def insert_assessment_db(self, values):
        try:
            cursor = self.connection.cursor()
            # Fetch course_id based on course_name
            cursor.execute("SELECT course_id FROM course WHERE course_name = %s", (values[0],))
            course_id = cursor.fetchone()[0]
            
            # Fetch instructor_id based on instructor_name
            cursor.execute("SELECT instructor_id FROM instructors WHERE instructor_name = %s", (values[3],))
            instructor_id = cursor.fetchone()[0]
            
            # Fetch student_id based on student_name
            cursor.execute("SELECT student_id FROM students WHERE student_name = %s", (values[4],))
            student_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO assessments (course_id, assessment_name, max_score, given_by, given_to) VALUES (%s, %s, %s, %s, %s)",
                           (course_id, values[1], values[2], instructor_id, student_id))
            self.connection.commit()
            messagebox.showinfo("Success", "Assessment inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error inserting assessment: {err}")

    def delete_instructor_db(self, instructor_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE instructors SET is_deleted = 'yes' WHERE instructor_name = %s", (instructor_name,))
            self.connection.commit()
            messagebox.showinfo("Success", f"Instructor '{instructor_name}' deleted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error deleting instructor: {err}")

    def delete_course_db(self, course_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE course SET is_deleted = 'yes' WHERE course_name = %s", (course_name,))
            self.connection.commit()
            messagebox.showinfo("Success", f"Course '{course_name}' deleted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error deleting course: {err}")

    def delete_student_db(self, student_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE students SET is_deleted = 'yes' WHERE student_name = %s", (student_name,))
            self.connection.commit()
            messagebox.showinfo("Success", f"Student '{student_name}' deleted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error deleting student: {err}")

    def delete_assessment_db(self, assessment_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE assessments SET is_deleted = 'yes' WHERE assessment_name = %s", (assessment_name,))
            self.connection.commit()
            messagebox.showinfo("Success", f"Assessment '{assessment_name}' deleted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error deleting assessment: {err}")

    def view_records_db(self, option):
        try:
            cursor = self.connection.cursor()
            if option == "View Instructors":
                cursor.execute("SELECT * FROM instructors WHERE is_deleted = 'no'")
            elif option == "View Courses":
                cursor.execute("SELECT * FROM course WHERE is_deleted = 'no'")
            elif option == "View Students":
                cursor.execute("SELECT * FROM students WHERE is_deleted = 'no'")
            elif option == "View Enrollments":
                cursor.execute("SELECT * FROM enrolments WHERE is_deleted = 'no'")
            elif option == "View Assessments":
                cursor.execute("SELECT * FROM assessments WHERE is_deleted = 'no'")
            records = cursor.fetchall()
            self.display_records(records)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error viewing records: {err}")

    def view_deleted_records_db(self, option):
        try:
            cursor = self.connection.cursor()
            if option == "View Deleted Instructors":
                cursor.execute("SELECT * FROM instructors WHERE is_deleted = 'yes'")
            elif option == "View Deleted Courses":
                cursor.execute("SELECT * FROM course WHERE is_deleted = 'yes'")
            elif option == "View Deleted Students":
                cursor.execute("SELECT * FROM students WHERE is_deleted = 'yes'")
            elif option == "View Deleted Assessments":
                cursor.execute("SELECT * FROM assessments WHERE is_deleted = 'yes'")
            records = cursor.fetchall()
            self.display_records(records)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error viewing deleted records: {err}")

    def display_records(self, records):
        self.result_text.delete(1.0, tk.END)
        if records:
            for record in records:
                self.result_text.insert(tk.END, str(record) + "\n")
        else:
            self.result_text.insert(tk.END, "No records found.\n")

    def fetch_instructors(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT instructor_name FROM instructors WHERE is_deleted = 'no'")
            instructors = [record[0] for record in cursor.fetchall()]
            return instructors
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching instructors: {err}")
            return None

    def fetch_courses(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT course_name FROM course WHERE is_deleted = 'no'")
            courses = [record[0] for record in cursor.fetchall()]
            return courses
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching courses: {err}")
            return None

    def fetch_students(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT student_name FROM students WHERE is_deleted = 'no'")
            students = [record[0] for record in cursor.fetchall()]
            return students
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching students: {err}")
            return None

    def fetch_assessments(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT assessment_name FROM assessments WHERE is_deleted = 'no'")
            assessments = [record[0] for record in cursor.fetchall()]
            return assessments
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching assessments: {err}")
            return None

    def search_records_button(self):
        search_term = simpledialog.askstring("Search Records", "Enter keyword to search:")
        if search_term:
            self.search_records(search_term)

    def search_records(self, keyword):
        try:
            cursor = self.connection.cursor()
            # Search in instructors, courses, students, enrollments, and assessments
            cursor.execute("SELECT * FROM instructors WHERE instructor_name LIKE %s AND is_deleted = 'no'", ('%' + keyword + '%',))
            instructors = cursor.fetchall()
            
            cursor.execute("SELECT * FROM course WHERE course_name LIKE %s AND is_deleted = 'no'", ('%' + keyword + '%',))
            courses = cursor.fetchall()
            
            cursor.execute("SELECT * FROM students WHERE student_name LIKE %s AND is_deleted = 'no'", ('%' + keyword + '%',))
            students = cursor.fetchall()
            
            cursor.execute("SELECT * FROM enrolments WHERE enrolment_date LIKE %s AND is_deleted = 'no'", ('%' + keyword + '%',))
            enrollments = cursor.fetchall()
            
            cursor.execute("SELECT * FROM assessments WHERE assessment_name LIKE %s AND is_deleted = 'no'", ('%' + keyword + '%',))
            assessments = cursor.fetchall()
            
            all_records = instructors + courses + students + enrollments + assessments
            self.display_records(all_records)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error searching records: {err}")

    def sort_instructors(self, sort_by):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM instructors WHERE is_deleted = 'no' ORDER BY {sort_by}")
            instructors = cursor.fetchall()
            self.display_records(instructors)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error sorting instructors: {err}")

    def sort_courses(self, sort_by):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM course WHERE is_deleted = 'no' ORDER BY {sort_by}")
            courses = cursor.fetchall()
            self.display_records(courses)
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error sorting courses: {err}")


if __name__ == "__main__":
    root = tk.Tk()
    db_gui = DatabaseGUI(root)
    root.mainloop()
