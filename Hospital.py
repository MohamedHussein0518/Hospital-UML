class Hospital:
    """
    Represents a hospital in the Hospital Management System.

    A Hospital has a name and a location, and contains a collection of
    Department objects (Hospital "contains" Department, relationship 1..*).

    Attributes:
        name (str): The name of the hospital.
        location (str): The physical location of the hospital.
        departments (list): A list of Department objects belonging to this hospital.
    """

    def __init__(self, name, location):
        """
        Initialize a new Hospital instance.

        Args:
            name (str): The name of the hospital.
            location (str): The location of the hospital.
        """
        self.name = name
        self.location = location
        self.departments = []  # Hospital contains multiple Departments (1..*)

    def add_department(self, department):
        """
        Add a Department object to this hospital's list of departments.

        Args:
            department (Department): The department to add to the hospital.

        Returns:
            None
        """
        self.departments.append(department)
        print(f"Department '{department.name}' added to {self.name}.")

    def view_info(self):
        """
        Get a formatted summary of the hospital's basic information.

        Returns:
            str: A string containing the hospital's name, location,
                 and number of departments.
        """
        return (f"Hospital Name: {self.name}\n"
                f"Location: {self.location}\n"
                f"Number of Departments: {len(self.departments)}")
