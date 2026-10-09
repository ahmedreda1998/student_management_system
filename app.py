# app.py - Streamlit Frontend (Main Application)

import streamlit as st
import json
import os
from hashlib import sha256
from database import Database
from student import Student
from chatbot import Chatbot, AdminChatbot

# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

CREDENTIALS_FILE = "credentials.json"
USERS_FILE = "users.json"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return sha256(password.encode()).hexdigest()


def load_json(filepath: str) -> dict:
    """Load data from a JSON file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def save_json(filepath: str, data: dict):
    """Save data to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def authenticate(username: str, password: str) -> str | None:
    """
    Authenticate a user against credentials.json for admins
    or users.json for regular users.
    Returns 'admin', 'user', or None.
    """
    hashed = hash_password(password)

    # Check all admin accounts in credentials.json
    admin_data = load_json(CREDENTIALS_FILE)

    for admin_key, admin_info in admin_data.items():
        if (
            admin_info.get("username") == username
            and admin_info.get("password") == hashed
        ):
            return "admin"

    # Check regular users in users.json
    users_data = load_json(USERS_FILE)

    if username in users_data:
        if users_data[username]["password"] == hashed:
            return "user"

    return None


def register_user(username: str, password: str, role: str = "user") -> tuple[bool, str]:
    """
    Register a new user.

    If role == 'admin', save to credentials.json.
    If role == 'user', save to users.json.
    """
    if not username or not password:
        return False, "Username and password cannot be empty."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users_data = load_json(USERS_FILE)
    admin_data = load_json(CREDENTIALS_FILE)

    # Check if username already exists in users.json
    if username in users_data:
        return False, "Username already exists as a normal user."

    # Check if username already exists in credentials.json
    for admin_key, admin_info in admin_data.items():
        if admin_info.get("username") == username:
            return False, "Username already exists as an admin."

    hashed_password = hash_password(password)

    if role == "admin":
        admin_data[username] = {
            "username": username,
            "password": hashed_password
        }
        save_json(CREDENTIALS_FILE, admin_data)
        return True, "✅ Admin registration successful! You can now log in as admin."

    else:
        users_data[username] = {
            "username": username,
            "password": hashed_password
        }
        save_json(USERS_FILE, users_data)
        return True, "✅ User registration successful! You can now log in."


# ─────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "page": "login",
        "chat_history": [],
        "db": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_db() -> Database:
    """Get or create a database connection stored in session state."""
    if st.session_state.db is None:
        st.session_state.db = Database(
            host="localhost",
            user="root",
            password="",
            database="student_db"
        )
    return st.session_state.db


# ─────────────────────────────────────────────────────────────
# Page: Login
# ─────────────────────────────────────────────────────────────

def page_login():
    st.title("🎓 Student Management System")
    st.subheader("🔐 Login")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input(
            "Password", type="password",
            placeholder="Enter your password"
        )
        col1, col2 = st.columns(2)
        login_btn = col1.form_submit_button("Login", use_container_width=True)
        register_btn = col2.form_submit_button("Register", use_container_width=True)

    if login_btn:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            role = authenticate(username, password)
            if role:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.session_state.page = "home"
                st.success(f"✅ Welcome, **{username}**! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    if register_btn:
        st.session_state.page = "register"
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Page: Register
# ─────────────────────────────────────────────────────────────

def page_register():
    st.title("🎓 Student Management System")
    st.subheader("📝 Create New Account")

    with st.form("register_form"):
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        role = st.selectbox(
            "Register as",
            ["user", "admin"]
        )

        admin_secret = ""

        if role == "admin":
            admin_secret = st.text_input(
                "Admin Secret Code",
                type="password",
                help="Enter the secret code required to create an admin account."
            )

        col1, col2 = st.columns(2)
        reg_btn = col1.form_submit_button("Register", use_container_width=True)
        back_btn = col2.form_submit_button(
            "Back to Login", use_container_width=True
        )

    if reg_btn:
        if password != confirm:
            st.error("❌ Passwords do not match.")

        elif role == "admin" and admin_secret != "admincode123":
            st.error("❌ Invalid admin secret code.")

        else:
            success, message = register_user(username, password, role)

            if success:
                st.success(message)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(f"❌ {message}")

    if back_btn:
        st.session_state.page = "login"
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Page: Admin Dashboard
# ─────────────────────────────────────────────────────────────

def page_admin_dashboard():
    db = get_db()
    st.title("🛠️ Admin Dashboard")
    st.write(f"👤 Logged in as: **{st.session_state.username}** (Admin)")

    # ── Sidebar Navigation ───────────────────────
    st.sidebar.title("📌 Navigation")
    section = st.sidebar.radio(
        "Go to",
        [
            "📊 Overview",
            "➕ Add Student",
            "📋 View Students",
            "✏️ Update Student",
            "🗑️ Delete Student",
            "🤖 Chatbot"
        ]
    )

    # ↓↓↓ Switch to User View Button ↓↓↓
    if st.sidebar.button("🔄 Switch to User View", use_container_width=True):
        st.session_state.role = "user"
        st.session_state.chat_history = []  # Reset chat history on switch
        st.rerun()
    # ↑↑↑ Switch to User View Button ↑↑↑

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    # ── Overview ─────────────────────────────────
    if section == "📊 Overview":
        st.subheader("📊 System Overview")
        total = db.get_total_students()
        students = db.fetch_students()

        col1, col2 = st.columns(2)
        col1.metric("Total Students", total)

        if students:
            grades = {}
            for s in students:
                grades[s.grade] = grades.get(s.grade, 0) + 1
            col2.write("**Grade Distribution:**")
            for grade, count in sorted(grades.items()):
                col2.write(f"- {grade}: {count} student(s)")
        else:
            col2.info("No students yet.")

    # ── Add Student ──────────────────────────────
    elif section == "➕ Add Student":
        st.subheader("➕ Add New Student")
        with st.form("add_student_form"):
            name = st.text_input("Student Name")
            age = st.number_input(
                "Age", min_value=1, max_value=120, value=18
            )
            grade = st.selectbox("Grade", ["A", "B", "C", "D", "F"])
            submitted = st.form_submit_button("Add Student")

        if submitted:
            if not name.strip():
                st.error("❌ Student name cannot be empty.")
            else:
                student = Student(
                    name=name.strip(),
                    age=int(age),
                    grade=grade
                )
                if db.insert_student(student):
                    st.success(f"✅ Student **{name}** added successfully!")
                else:
                    st.error(
                        "❌ Failed to add student. Check database connection."
                    )

    # ── View Students ────────────────────────────
    elif section == "📋 View Students":
        st.subheader("📋 All Students")
        students = db.fetch_students()
        if students:
            data = [s.to_dict() for s in students]
            st.dataframe(
                data,
                use_container_width=True,
                column_config={
                    "student_id": "ID",
                    "name": "Name",
                    "age": "Age",
                    "grade": "Grade"
                }
            )
            st.info(f"Total: **{len(students)}** student(s)")
        else:
            st.info("📭 No students found in the database.")

    # ── Update Student ───────────────────────────
    elif section == "✏️ Update Student":
        st.subheader("✏️ Update Student")
        students = db.fetch_students()
        if not students:
            st.info("No students to update.")
        else:
            options = {
                f"ID {s.student_id}: {s.name}": s for s in students
            }
            selected = st.selectbox("Select Student", list(options.keys()))
            student = options[selected]

            with st.form("update_form"):
                new_name = st.text_input("Name", value=student.name)
                new_age = st.number_input(
                    "Age", min_value=1, max_value=120,
                    value=student.age
                )
                grade_opts = ["A", "B", "C", "D", "F"]
                current_idx = (
                    grade_opts.index(student.grade)
                    if student.grade in grade_opts else 0
                )
                new_grade = st.selectbox(
                    "Grade", grade_opts, index=current_idx
                )
                update_btn = st.form_submit_button("Update Student")

            if update_btn:
                student.update(
                    name=new_name,
                    age=int(new_age),
                    grade=new_grade
                )
                if db.update_student(student):
                    st.success(
                        f"✅ Student **{new_name}** updated successfully!"
                    )
                else:
                    st.error("❌ Update failed.")

    # ── Delete Student ───────────────────────────
    elif section == "🗑️ Delete Student":
        st.subheader("🗑️ Delete Student")
        students = db.fetch_students()
        if not students:
            st.info("No students to delete.")
        else:
            options = {
                f"ID {s.student_id}: {s.name}": s for s in students
            }
            selected = st.selectbox(
                "Select Student to Delete", list(options.keys())
            )
            student = options[selected]

            st.warning(
                f"⚠️ You are about to delete "
                f"**{student.name}** (ID: {student.student_id})"
            )
            col1, col2 = st.columns(2)

            if col1.button("🗑️ Confirm Delete", type="primary"):
                if db.delete_student(student.student_id):
                    st.success(f"✅ Student **{student.name}** deleted.")
                    st.rerun()
                else:
                    st.error("❌ Deletion failed.")

            if col2.button("Cancel"):
                st.info("Deletion cancelled.")

    # ── Admin Chatbot ────────────────────────────
    elif section == "🤖 Chatbot":
        page_chatbot(role="admin")


# ─────────────────────────────────────────────────────────────
# Page: User Dashboard
# ─────────────────────────────────────────────────────────────

def page_user_dashboard():
    st.title("🎓 Student Portal")
    st.write(f"👤 Logged in as: **{st.session_state.username}** (User)")

    st.sidebar.title("📌 Navigation")
    section = st.sidebar.radio(
        "Go to",
        [
            "📋 View Students",
            "🤖 Chatbot"
        ]
    )

    # ↓↓↓ Switch to Admin View Button ↓↓↓
    if st.sidebar.button("🔄 Switch to Admin View", use_container_width=True):
        st.session_state.role = "admin"
        st.session_state.chat_history = []  # Reset chat history on switch
        st.rerun()
    # ↑↑↑ Switch to Admin View Button ↑↑↑

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()

    db = get_db()

    if section == "📋 View Students":
        st.subheader("📋 Student Directory")
        students = db.fetch_students()
        if students:
            data = [s.to_dict() for s in students]
            st.dataframe(
                data,
                use_container_width=True,
                column_config={
                    "student_id": "ID",
                    "name": "Name",
                    "age": "Age",
                    "grade": "Grade"
                }
            )
            st.info(f"Total: **{len(students)}** student(s)")
        else:
            st.info("📭 No students found.")

    elif section == "🤖 Chatbot":
        page_chatbot(role="user")


# ─────────────────────────────────────────────────────────────
# Shared: Chatbot Page
# ─────────────────────────────────────────────────────────────

def page_chatbot(role: str = "user"):
    db = get_db()
    bot = AdminChatbot(db) if role == "admin" else Chatbot(db)

    st.subheader(f"🤖 {bot.bot_name}")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show greeting on first load
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": bot.greet()
        })

    # Render chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    user_input = st.chat_input("Ask me something about students...")
    if user_input:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get bot response
        response = bot.get_response(user_input)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        with st.chat_message("assistant"):
            st.markdown(response)

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────

def logout():
    """Clear session and return to login."""
    for key in ["logged_in", "username", "role", "chat_history"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.page = "login"
    st.session_state.logged_in = False
    if st.session_state.get("db"):
        st.session_state.db.close()
        st.session_state.db = None
    st.rerun()


# ─────────────────────────────────────────────────────────────
# Main App Router
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Student Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="auto"
    )

    init_session()

    # Route to appropriate page
    if not st.session_state.logged_in:
        if st.session_state.page == "register":
            page_register()
        else:
            page_login()
    else:
        if st.session_state.role == "admin":
            page_admin_dashboard()
        else:
            page_user_dashboard()


if __name__ == "__main__":
    main()