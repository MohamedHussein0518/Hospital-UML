import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttkb

from Department import Department
from patient import Patient
from Staff import Staff


class RecordDialog(ttkb.Toplevel):
    """Base class for the modal Add/Edit record forms.

    Subclasses build fields with field()/spinbox()/combobox()/multiline(),
    then call finish() to wire up the Save/Cancel row. After
    `self.wait_window(dialog)`, callers should check `dialog.result` — it is
    only True if the user saved with valid data.
    """

    def __init__(self, parent, title: str, size: str = "420x560"):
        super().__init__(title=title)
        self.geometry(size)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = False
        self._enter_bindable = []

        self.container = ttkb.Frame(self, padding=24)
        self.container.pack(fill="both", expand=True)

        self.bind("<Escape>", lambda _e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def heading(self, text: str):
        ttkb.Label(self.container, text=text, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 6))

    def field(self, label_text: str) -> ttkb.Entry:
        ttkb.Label(self.container, text=label_text, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 3))
        entry = ttkb.Entry(self.container)
        entry.pack(fill="x")
        self._enter_bindable.append(entry)
        return entry

    def spinbox(self, label_text: str, from_: int, to: int) -> ttkb.Spinbox:
        ttkb.Label(self.container, text=label_text, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 3))
        spin = ttkb.Spinbox(self.container, from_=from_, to=to)
        spin.pack(fill="x")
        self._enter_bindable.append(spin)
        return spin

    def combobox(self, label_text: str, values: list[str]) -> ttkb.Combobox:
        ttkb.Label(self.container, text=label_text, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 3))
        combo = ttkb.Combobox(self.container, values=values, state="readonly")
        combo.pack(fill="x")
        if values:
            combo.current(0)
        self._enter_bindable.append(combo)
        return combo

    def multiline(self, label_text: str, height: int = 5) -> tk.Text:
        # Deliberately not in _enter_bindable: Enter must insert a newline here, not submit.
        ttkb.Label(self.container, text=label_text, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 3))
        text = tk.Text(self.container, height=height, font=("Segoe UI", 10), wrap="word", relief="solid", borderwidth=1)
        text.pack(fill="x")
        return text

    def finish(self, save_text: str, on_save):
        row = ttkb.Frame(self.container)
        row.pack(fill="x", pady=(20, 0))
        ttkb.Button(row, text="Cancel", style="Secondary.TButton", command=self._cancel).pack(side="right", padx=(8, 0))
        ttkb.Button(row, text=save_text, style="Primary.TButton", command=on_save).pack(side="right")
        for widget in self._enter_bindable:
            widget.bind("<Return>", lambda _e: on_save())

    def _cancel(self):
        self.result = False
        self.destroy()

    def accept(self):
        self.result = True
        self.destroy()


class PatientDialog(RecordDialog):
    """Add or edit a patient. Pass `patient`/`department_name` to pre-fill for editing."""

    def __init__(self, parent, patient: Patient = None, department_name: str = None):
        super().__init__(parent, "Edit Patient" if patient else "Add Patient")
        self.heading("Edit Patient Details" if patient else "Register New Patient")

        self.name_entry = self.field("Full Name")
        self.age_spin = self.spinbox("Age", 0, 120)
        self.record_text = self.multiline("Medical Record")
        self.department_combo = self.combobox("Department", Department.DEPARTMENTS)

        if patient:
            self.name_entry.insert(0, patient.name)
            self.age_spin.set(patient.age)
            self.record_text.insert("1.0", patient.medical_record)
            if department_name in Department.DEPARTMENTS:
                self.department_combo.set(department_name)

        self.finish("Save Patient", self._save)

    def _save(self):
        name = self.name_entry.get().strip()
        age_text = str(self.age_spin.get()).strip()
        medical_record = self.record_text.get("1.0", "end").strip()
        department_name = self.department_combo.get().strip()

        if not department_name:
            messagebox.showwarning("Missing Data", "Please select a department.", parent=self)
            return
        try:
            age = int(age_text)
        except ValueError:
            messagebox.showerror("Invalid Age", "Age must be a whole number.", parent=self)
            return

        try:
            self.patient = Patient(name, age, medical_record)
        except ValueError as exc:
            messagebox.showerror("Invalid Data", str(exc), parent=self)
            return

        self.department_name = department_name
        self.accept()


class StaffDialog(RecordDialog):
    """Add or edit a staff member. Pass `staff_member`/`department_name` to pre-fill for editing."""

    def __init__(self, parent, staff_member: Staff = None, department_name: str = None):
        super().__init__(parent, "Edit Staff" if staff_member else "Add Staff")
        self.heading("Edit Staff Details" if staff_member else "Add Staff Member")

        self.name_entry = self.field("Name")
        self.age_spin = self.spinbox("Age", 0, 120)
        self.position_combo = self.combobox("Position", Staff.POSITIONS)
        self.department_combo = self.combobox("Department", Department.DEPARTMENTS)

        if staff_member:
            self.name_entry.insert(0, staff_member.name)
            self.age_spin.set(staff_member.age)
            self.position_combo.set(staff_member.position)
            if department_name in Department.DEPARTMENTS:
                self.department_combo.set(department_name)

        self.finish("Save Staff", self._save)

    def _save(self):
        name = self.name_entry.get().strip()
        age_text = str(self.age_spin.get()).strip()
        position = self.position_combo.get().strip()
        department_name = self.department_combo.get().strip()

        if not position or not department_name:
            messagebox.showwarning("Missing Data", "Please select a position and department.", parent=self)
            return
        try:
            age = int(age_text)
        except ValueError:
            messagebox.showerror("Invalid Age", "Age must be a whole number.", parent=self)
            return

        try:
            self.staff_member = Staff(name, age, position)
        except ValueError as exc:
            messagebox.showerror("Invalid Data", str(exc), parent=self)
            return

        self.department_name = department_name
        self.accept()
