from person import Person  

class Patient(Person):
    """Class for hospital patients, inheriting from Person."""
    
    def __init__(self, name: str, age: int, medical_record: str):
        super().__init__(name, age)
        self.medical_record = medical_record

    def view_record(self) -> str:
        """View patient record."""
        return f"Patient Record: {self.medical_record}"
