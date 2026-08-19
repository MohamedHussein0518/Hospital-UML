from patient import Patient
from Staff import Staff


class Department:
    """
    Represents a department in the hospital.

    Departments are a fixed set (Department.DEPARTMENTS) — the single source
    of truth for which departments exist across the whole app.

    Attributes:
        name (str): The name of the department.
        patients (list[Patient]): A list of patients in the department.
        staff (list[Staff]): A list of staff members in the department.
    """

    DEPARTMENTS = [
        "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Emergency",
        "Radiology", "Oncology", "Intensive Care", "Surgery", "Dermatology",
    ]

    def __init__(self, name: str):
        """
        Initialize a new Department.

        Args:
            name (str): The name of the department. Must be one of
                Department.DEPARTMENTS.
        """
        if name not in Department.DEPARTMENTS:
            raise ValueError(f"'{name}' is not a recognized department.")
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

    def remove_patient(self, patient: Patient) -> None:
        """Remove a patient from the department."""
        self.patients.remove(patient)

    def remove_staff(self, staff_member: Staff) -> None:
        """Remove a staff member from the department."""
        self.staff.remove(staff_member)
