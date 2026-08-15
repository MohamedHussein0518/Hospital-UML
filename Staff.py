from person import Person  

class Staff(Person):
    """Represents a staff member in a hospital.

    Inherits name and age from the Person class and adds
    a position attribute for the staff member's job role.
    """

    def __init__(self, name, age, position):
        """Initialize a Staff object.

        Args:
            name (str): The staff member's name.
            age (int): The staff member's age.
            position (str): The staff member's job position.
        """
        super().__init__(name, age)
        self.position = position

    def view_info(self):
        """Return the staff member's information.

        Returns:
            str: The name, age, and position of the staff member.
        """
        return f"Name: {self.name}, Age: {self.age}, Position: {self.position}"