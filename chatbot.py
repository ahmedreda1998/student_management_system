# chatbot.py - Chatbot Class (OOP - Abstraction & Polymorphism)

from database import Database


class Chatbot:
    """
    Simulates an AI-driven chatbot that responds to student-related queries.
    Abstracts query handling logic. Can be extended via inheritance (Polymorphism).
    Demonstrates Abstraction, Encapsulation, and Polymorphism OOP principles.
    """

    def __init__(self, db: Database):
        self.db = db
        self.bot_name = "RedaBot"

    def greet(self) -> str:
        """Return a greeting message."""
        return (f"👋 Hello! I'm **{self.bot_name}**, your student management assistant.\n"
                "You can ask me things like:\n"
                "- *How many students are there?*\n"
                "- *Show all students*\n"
                "- *Find student named [name]*\n"
                "- *What is the grade of student [name]?*\n"
                "- *How old is student [name]?*")

    def get_response(self, user_input: str) -> str:
        """
        Generate a response based on user input.
        This method can be overridden in subclasses (Polymorphism).
        """
        query = user_input.lower().strip()

        # ── Total count ──────────────────────────────
        if any(kw in query for kw in ["how many", "total", "count"]):
            total = self.db.get_total_students()
            return f"📊 There are currently **{total}** student(s) in the system."

        # ── List all students ────────────────────────
        if any(kw in query for kw in ["show all", "list all", "all students",
                                       "fetch all", "display all"]):
            students = self.db.fetch_students()
            if not students:
                return "📭 No students found in the database."
            response = "📋 **All Students:**\n"
            for s in students:
                response += (f"- **ID:** {s.student_id} | **Name:** {s.name} "
                             f"| **Age:** {s.age} | **Grade:** {s.grade}\n")
            return response

        # ── Find by name ─────────────────────────────
        if any(kw in query for kw in ["find", "search", "look up", "who is"]):
            name = self._extract_name(query)
            if name:
                students = self.db.fetch_student_by_name(name)
                if students:
                    response = f"🔍 Found **{len(students)}** result(s) for '{name}':\n"
                    for s in students:
                        response += (f"- **ID:** {s.student_id} | **Name:** {s.name} "
                                     f"| **Age:** {s.age} | **Grade:** {s.grade}\n")
                    return response
                return f"❌ No student found with the name '{name}'."
            return "⚠️ Please specify a student name. E.g., *Find student named John*"

        # ── Grade query ──────────────────────────────
        if "grade" in query:
            name = self._extract_name(query)
            if name:
                students = self.db.fetch_student_by_name(name)
                if students:
                    s = students[0]
                    return f"📝 **{s.name}**'s grade is: **{s.grade}**"
                return f"❌ No student found with the name '{name}'."
            return "⚠️ Please specify a student name."

        # ── Age query ────────────────────────────────
        if "age" in query or "old" in query:
            name = self._extract_name(query)
            if name:
                students = self.db.fetch_student_by_name(name)
                if students:
                    s = students[0]
                    return f"🎂 **{s.name}** is **{s.age}** years old."
                return f"❌ No student found with the name '{name}'."
            return "⚠️ Please specify a student name."

        # ── Help ─────────────────────────────────────
        if any(kw in query for kw in ["help", "what can you do", "commands"]):
            return self.greet()

        # ── Greetings ────────────────────────────────
        if any(kw in query for kw in ["hello", "hi", "hey", "greet"]):
            return f"👋 Hello! I'm {self.bot_name}. How can I help you today?"

        # ── Default fallback ─────────────────────────
        return ("🤔 I'm not sure how to answer that yet. Try asking:\n"
                "- *Show all students*\n"
                "- *How many students are there?*\n"
                "- *Find student named [name]*")

    def _extract_name(self, query: str) -> str | None:
        """Extract a name from the user query using keyword triggers."""
        triggers = ["named", "called", "of student", "of", "is", "student"]
        for trigger in triggers:
            if trigger in query:
                parts = query.split(trigger)
                if len(parts) > 1:
                    name = parts[-1].strip().rstrip("?.,!")
                    if name:
                        return name.title()
        return None


# ── Subclass demonstrating Inheritance & Polymorphism ──────────────────────
class AdminChatbot(Chatbot):
    """
    Extended chatbot for admin users with additional capabilities.
    Demonstrates Inheritance and Polymorphism.
    """

    def __init__(self, db: Database):
        super().__init__(db)
        self.bot_name = "AdminBot"

    def get_response(self, user_input: str) -> str:
        """Override get_response to add admin-specific responses."""
        query = user_input.lower().strip()

        if "summary" in query or "report" in query:
            students = self.db.fetch_students()
            total = len(students)
            if total == 0:
                return "📊 No students in the system yet."
            grades = {}
            for s in students:
                grades[s.grade] = grades.get(s.grade, 0) + 1
            report = f"📊 **System Report:**\n- Total Students: **{total}**\n"
            report += "- Grade Distribution:\n"
            for grade, count in sorted(grades.items()):
                report += f"  • {grade}: {count} student(s)\n"
            return report

        # Fall back to base class response
        return super().get_response(user_input)