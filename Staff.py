from person import Person


class Staff(Person):
    """Represents a staff member in a hospital.

    Inherits name and age from the Person class and adds
    a position attribute for the staff member's job role.
    """

    POSITIONS = ["Doctor", "Nurse", "Technician", "Receptionist", "Administrator"]

    def __init__(self, name, age, position):
        """Initialize a Staff object.

        Args:
            name (str): The staff member's name.
            age (int): The staff member's age.
            position (str): The staff member's job position.
        """
        super().__init__(name, age)
        self.position = position

    @property
    def position(self) -> str:
        return self._position

    @position.setter
    def position(self, value):
        if value not in Staff.POSITIONS:
            raise ValueError(f"Position must be one of: {', '.join(Staff.POSITIONS)}.")
        self._position = value

    def view_info(self):
        """Return the staff member's information.

        Returns:
            str: The name, age, and position of the staff member.
        """
        return f"Name: {self.name}, Age: {self.age}, Position: {self.position}"
