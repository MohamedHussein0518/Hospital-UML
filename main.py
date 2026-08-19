from config import HOSPITAL_NAME, HOSPITAL_LOCATION
from Hospital import Hospital
from Department import Department
from patient import Patient
from Staff import Staff


def main():
    hospital = Hospital(HOSPITAL_NAME, HOSPITAL_LOCATION)

    cardiology = Department("Cardiology")
    neurology = Department("Neurology")

    hospital.add_department(cardiology)
    hospital.add_department(neurology)

    patient1 = Patient("Ahmed Ali", 45, "MR-001: Hypertension")
    patient2 = Patient("Sara Youssef", 30, "MR-002: Arrhythmia")
    doctor1 = Staff("Dr. Omar Khaled", 50, "Doctor")
    nurse1 = Staff("Mona Adel", 28, "Nurse")

    cardiology.add_patient(patient1)
    cardiology.add_patient(patient2)
    cardiology.add_staff(doctor1)
    cardiology.add_staff(nurse1)

    print(hospital.view_info())
    print()

    for department in hospital.departments:
        print(f"Department: {department.name}")

        print("  Staff:")
        for staff_member in department.staff:
            print(f"    - {staff_member.view_info()}")

        print("  Patients:")
        for patient in department.patients:
            print(f"    - {patient.view_info()}")
            print(f"      {patient.view_record()}")
        print()


if __name__ == "__main__":
    main()
