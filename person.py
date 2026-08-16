class Person:
    """Base class for all people in the hospital."""
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def view_info(self) -> str:
        """View basic information about the person."""
        return f"Name: {self.name}, Age: {self.age}"
person = Person("Maha", 20)

print(person.view_info())