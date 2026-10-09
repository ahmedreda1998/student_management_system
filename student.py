class Student:
    """
    Represents a student entity with attributes and update functionality.
    Demonstrates Encapsulation and Abstraction OOP principles.
    """

    def __init__(self, student_id=None, name=None, age=None, grade=None):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade

    def update(self, name=None, age=None, grade=None):
        """Update student attributes if new values are provided."""
        if name:
            self.name = name
        if age:
            self.age = age
        if grade:
            self.grade = grade

    def to_dict(self):
        """Convert student object to dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "grade": self.grade
        }

    def __repr__(self):
        return (f"Student(id={self.student_id}, name={self.name}, "
                f"age={self.age}, grade={self.grade})")
    
        