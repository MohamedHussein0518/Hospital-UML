class Person:
    """Base class for all people in the hospital."""

    MIN_AGE = 0
    MAX_AGE = 120

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError("Name is required.")
        self._name = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Age must be a whole number.")
        if not (Person.MIN_AGE <= value <= Person.MAX_AGE):
            raise ValueError(f"Age must be between {Person.MIN_AGE} and {Person.MAX_AGE}.")
        self._age = value

    def view_info(self) -> str:
        """View basic information about the person."""
        return f"Name: {self.name}, Age: {self.age}"
