class Department:
    """
    Represents a department in the hospital.

    Attributes:
        name (str): The name of the department.
        patients (list[Patient]): A list of patients in the department.
        staff (list[Staff]): A list of staff members in the department.
    """

    def __init__(self, name: str):
        """
        Initialize a new Department.

        Args:
            name (str): The name of the department.
        """
        self.name = name
        self.patients = []
        self.staff = []

    def add_patient(self, patient: Patient) -> None:
        """
        Add a patient to the department.

        Args:
            patient (Patient): The patient to be added.
        """
        self.patients.append(patient)

    def add_staff(self, staff_member: Staff) -> None:
        """
        Add a staff member to the department.

        Args:
            staff_member (Staff): The staff member to be added.
        """
        self.staff.append(staff_member)