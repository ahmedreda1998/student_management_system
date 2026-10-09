# database.py - Database Class (OOP - Abstraction & Encapsulation)

import mysql.connector
from mysql.connector import Error
from student import Student


class Database:
    """
    Manages all MySQL database interactions.
    Abstracts complex SQL operations into simple methods.
    Demonstrates Abstraction and Encapsulation OOP principles.
    """

    def __init__(self, host="localhost", user="root",
                 password="", database="student_db"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Establish connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("✅ Connected to MySQL database.")
        except Error as e:
            print(f"❌ Database connection error: {e}")
            self.connection = None

    def _create_table(self):
        """Create the students table if it does not exist."""
        query = """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            grade VARCHAR(50)
        );
        """
        self._execute_query(query)

    def _execute_query(self, query, params=None):
        """Execute a write query (INSERT, UPDATE, DELETE, CREATE)."""
        if not self.connection or not self.connection.is_connected():
            self._connect()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Query execution error: {e}")
            return False

    def _fetch_query(self, query, params=None):
        """Execute a read query (SELECT) and return results."""
        if not self.connection or not self.connection.is_connected():
            self._connect()
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"❌ Fetch error: {e}")
            return []

    # ──────────────────────────────────────────────
    # Public CRUD Methods (Abstracted Interface)
    # ──────────────────────────────────────────────

    def insert_student(self, student: Student) -> bool:
        """Insert a new student record into the database."""
        query = "INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)"
        return self._execute_query(query, (student.name, student.age, student.grade))

    def fetch_students(self) -> list[Student]:
        """Retrieve all students from the database."""
        rows = self._fetch_query("SELECT * FROM students")
        return [Student(r["id"], r["name"], r["age"], r["grade"]) for r in rows]

    def fetch_student_by_id(self, student_id: int) -> Student | None:
        """Retrieve a single student by their ID."""
        rows = self._fetch_query(
            "SELECT * FROM students WHERE id = %s", (student_id,)
        )
        if rows:
            r = rows[0]
            return Student(r["id"], r["name"], r["age"], r["grade"])
        return None

    def fetch_student_by_name(self, name: str) -> list[Student]:
        """Retrieve students matching a name (case-insensitive)."""
        rows = self._fetch_query(
            "SELECT * FROM students WHERE name LIKE %s", (f"%{name}%",)
        )
        return [Student(r["id"], r["name"], r["age"], r["grade"]) for r in rows]

    def update_student(self, student: Student) -> bool:
        """Update an existing student's details."""
        query = """
        UPDATE students SET name=%s, age=%s, grade=%s WHERE id=%s
        """
        return self._execute_query(
            query, (student.name, student.age, student.grade, student.student_id)
        )

    def delete_student(self, student_id: int) -> bool:
        """Delete a student record by ID."""
        return self._execute_query(
            "DELETE FROM students WHERE id=%s", (student_id,)
        )

    def get_total_students(self) -> int:
        """Return the total number of students."""
        rows = self._fetch_query("SELECT COUNT(*) AS total FROM students")
        return rows[0]["total"] if rows else 0

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Database connection closed.")