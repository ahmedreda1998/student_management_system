# 🎓 Student Management System

A Streamlit web app for managing student records, with role-based login (admin/user), a MySQL-backed database layer, and a simple rule-based chatbot for querying student data in natural language.

## Features

- **Authentication** — Login and registration for two roles: `admin` and `user`. Admin registration requires a secret code. Passwords are hashed with SHA-256 before being stored.
- **Admin Dashboard**
  - Overview with total student count and grade distribution
  - Add, view, update, and delete student records
  - Switch to the user view without logging out
- **User Dashboard**
  - Read-only student directory
  - Switch to the admin view
- **Chatbot Assistant** — Ask questions like "How many students are there?", "Show all students", "Find student named John", "What is the grade of student John?". Admins get an extended `AdminChatbot` that can also generate a grade-distribution summary/report.

## Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Backend/Storage:** MySQL (via `mysql-connector-python`)
- **Auth storage:** Local JSON files (`credentials.json` for admins, `users.json` for regular users)
- **Language:** Python 3

## Project Structure

```
student_management_system/
├── app.py              # Streamlit frontend — routing, auth, pages (login/register/dashboards/chatbot)
├── database.py         # Database class — MySQL connection and CRUD operations (abstraction layer)
├── student.py          # Student class — the student entity model
├── chatbot.py          # Chatbot / AdminChatbot classes — rule-based query handling
├── credentials.json    # Admin accounts (username + hashed password) — created at runtime
├── users.json           # Regular user accounts (username + hashed password) — created at runtime
└── README.md
```

## Object-Oriented Design

The project is organized around a few core classes to demonstrate OOP principles:

- `Student` (`student.py`) — Encapsulation & Abstraction. Holds student data and exposes `update()` and `to_dict()`.
- `Database` (`database.py`) — Abstraction & Encapsulation. Wraps all MySQL queries (connect, create table, insert/fetch/update/delete) behind a simple method-based interface.
- `Chatbot` / `AdminChatbot` (`chatbot.py`) — Inheritance & Polymorphism. `AdminChatbot` extends `Chatbot` and overrides `get_response()` to add admin-only capabilities (e.g. system reports) while falling back to the base implementation for everything else.

## Setup

### 1. Prerequisites

- Python 3.10+
- A running MySQL server (default connection assumes `host=localhost`, `user=root`, no password — see `get_db()` in `app.py`)

### 2. Install dependencies

```bash
pip install streamlit mysql-connector-python
```

### 3. Database

No manual setup is required beyond having MySQL running — `Database.__init__` connects to (or creates) the `student_db` database context and automatically creates the `students` table if it doesn't exist. Adjust host/user/password/database in `get_db()` in `app.py` if your MySQL credentials differ.

### 4. Run the app

```bash
streamlit run app.py
```

The app opens in your browser (default: `http://localhost:8501`).

## Usage

1. **Register** an account from the login screen. Choose role `user` or `admin`.
   - Registering as `admin` requires the secret code `admincode123` (set in `app.py`, change before any real deployment).
2. **Log in** with your username/password.
3. **Admins** can add, view, update, and delete students, see a dashboard overview, and chat with `AdminBot`.
4. **Users** can view the student directory and chat with `RedaBot`.
5. Either role can switch views via the sidebar button, and both can chat with the bot about student data (e.g. counts, lookups by name, grades, ages).

## Security Notes

This project is intended as a learning/demo app, not production-ready:

- The admin secret code is hard-coded in plain text in `app.py`.
- User/admin credentials are stored in plain JSON files on disk (passwords are hashed, but there's no salting, rate limiting, or session security beyond Streamlit's session state).
- Default MySQL connection uses the `root` user with no password.

Harden these before using the app with real data.
# student_management_system
