import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttkb

from config import HOSPITAL_NAME, HOSPITAL_LOCATION
from Hospital import Hospital
from Department import Department
from patient import Patient
from Staff import Staff
from patient_store import PatientRecordStore
from staff_store import StaffRecordStore
from dialogs import PatientDialog, StaffDialog

# ---------------------------------------------------------------------------
# Design tokens — the single source of truth for color/spacing across the app.
# Every widget below is styled from this dict; nothing hardcodes a hex value.
# ---------------------------------------------------------------------------
COLORS = {
    "sidebar_bg": "#0F172A",
    "sidebar_hover": "#1E293B",
    "sidebar_active": "#1E293B",
    "sidebar_accent": "#3B82F6",
    "sidebar_text": "#94A3B8",
    "sidebar_text_active": "#FFFFFF",
    "canvas": "#F8FAFC",
    "card_bg": "#FFFFFF",
    "card_border": "#E2E8F0",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "secondary_border": "#CBD5E1",
    "secondary_text": "#334155",
    "danger_text": "#DC2626",
    "danger_hover_bg": "#FEF2F2",
    "text_primary": "#0F172A",
    "text_muted": "#64748B",
    "table_header_bg": "#F1F5F9",
    "table_header_text": "#475569",
    "row_stripe": "#F8FAFC",
    "row_selected": "#EFF6FF",
    "success_text": "#16A34A",
}

FONT_BODY = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_KPI = ("Segoe UI", 28, "bold")

NAV_ITEMS = ["Dashboard", "Departments", "Patients", "Staff"]

KPI_TOKENS = [
    ("Departments", "D", "#DBEAFE", "#2563EB"),
    ("Patients", "P", "#DCFCE7", "#16A34A"),
    ("Staff", "S", "#EDE9FE", "#7C3AED"),
]


def configure_styles(style: ttkb.Style):
    """Central style configuration. This is the app's only stylesheet — every
    other widget below refers back to these registered style names/tokens
    instead of setting its own look inline."""
    style.configure(".", font=FONT_BODY)
    style.configure("TFrame", background=COLORS["canvas"])
    style.configure("TLabel", background=COLORS["canvas"], foreground=COLORS["text_primary"], font=FONT_BODY)

    style.configure(
        "Primary.TButton", background=COLORS["primary"], foreground="white",
        font=("Segoe UI", 10, "bold"), padding=(16, 8), borderwidth=0,
    )
    style.map("Primary.TButton", background=[("active", COLORS["primary_hover"]), ("pressed", COLORS["primary_hover"])])

    style.configure(
        "Secondary.TButton", background="white", foreground=COLORS["secondary_text"],
        font=FONT_BODY, padding=(16, 8), borderwidth=1, relief="solid",
    )
    style.map("Secondary.TButton", background=[("active", COLORS["canvas"])])

    style.configure(
        "Danger.TButton", background="white", foreground=COLORS["danger_text"],
        font=FONT_BODY, padding=(16, 8), borderwidth=0,
    )
    style.map("Danger.TButton", background=[("active", COLORS["danger_hover_bg"])])

    style.configure(
        "Treeview", background="white", fieldbackground="white", foreground=COLORS["text_primary"],
        rowheight=40, font=FONT_BODY, borderwidth=1, bordercolor=COLORS["card_border"],
    )
    style.configure(
        "Treeview.Heading", background=COLORS["table_header_bg"], foreground=COLORS["table_header_text"],
        font=("Segoe UI", 10, "bold"), relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["row_selected"])],
        foreground=[("selected", COLORS["text_primary"])],
    )


def make_table(parent, columns, headings, widths):
    """Build a striped, scrollable Treeview and return it. Callers always
    redraw it from the model (delete + reinsert) — never append a lone row."""
    frame = ttkb.Frame(parent)
    frame.pack(fill="both", expand=True)

    tree = ttkb.Treeview(frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="w", stretch=True)
    tree.tag_configure("odd", background=COLORS["row_stripe"])
    tree.tag_configure("empty", foreground=COLORS["text_muted"])
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttkb.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    return tree


def fill_table(tree, rows, empty_text=None):
    tree.delete(*tree.get_children())
    if not rows:
        if empty_text:
            column_count = len(tree["columns"])
            tree.insert("", "end", values=[empty_text] + [""] * (column_count - 1), tags=("empty",))
        return
    for i, row in enumerate(rows):
        tree.insert("", "end", values=row, tags=("odd",) if i % 2 else ())


def make_card(parent, padding=20):
    """A white, bordered panel. Returns (outer_frame_to_pack, inner_content_frame)."""
    outer = tk.Frame(parent, bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"], highlightthickness=1, bd=0)
    inner = tk.Frame(outer, bg=COLORS["card_bg"])
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    return outer, inner


class HospitalApp(ttkb.Window):
    """Multi-page hospital management dashboard (Dashboard / Departments / Patients / Staff).

    Departments are fixed (Department.DEPARTMENTS) and all exist from startup.
    Dialogs never touch the tables directly — they hand back a validated
    domain object, the app mutates the Hospital model, and the page redraws
    its table from that model.
    """

    def __init__(self):
        super().__init__(
            title="Hospital Management System",
            themename="cosmo",
            size=(1150, 760),
            minsize=(1000, 680),
            resizable=(True, True),
        )

        configure_styles(self.style)
        self.configure(background=COLORS["canvas"])

        self.hospital = Hospital(HOSPITAL_NAME, HOSPITAL_LOCATION)
        self.departments: dict[str, Department] = {}
        for name in Department.DEPARTMENTS:
            department = Department(name)
            self.departments[name] = department
            self.hospital.add_department(department)

        self.patient_store = PatientRecordStore()
        self.staff_store = StaffRecordStore()

        self.active_page = "Dashboard"
        self.nav_rows: dict[str, tuple] = {}
        self._status_after_id = None

        self._build_sidebar()
        self._build_content_shell()
        self._build_statusbar()

        self._load_data()
        self.show_page("Dashboard")
        self.state("zoomed")

    # ---------- domain / data layer ----------
    def add_patient(self, patient: Patient, department_name: str) -> None:
        self.departments[department_name].add_patient(patient)
        self._persist_patients()

    def update_patient(self, old_patient: Patient, old_department_name: str, new_patient: Patient, new_department_name: str) -> None:
        self.departments[old_department_name].remove_patient(old_patient)
        self.departments[new_department_name].add_patient(new_patient)
        self._persist_patients()

    def delete_patient(self, patient: Patient, department_name: str) -> None:
        self.departments[department_name].remove_patient(patient)
        self._persist_patients()

    def add_staff(self, staff_member: Staff, department_name: str) -> None:
        self.departments[department_name].add_staff(staff_member)
        self._persist_staff()

    def update_staff(self, old_staff: Staff, old_department_name: str, new_staff: Staff, new_department_name: str) -> None:
        self.departments[old_department_name].remove_staff(old_staff)
        self.departments[new_department_name].add_staff(new_staff)
        self._persist_staff()

    def delete_staff(self, staff_member: Staff, department_name: str) -> None:
        self.departments[department_name].remove_staff(staff_member)
        self._persist_staff()

    def counts(self) -> tuple[int, int, int]:
        total_patients = sum(len(d.patients) for d in self.hospital.departments)
        total_staff = sum(len(d.staff) for d in self.hospital.departments)
        return len(self.hospital.departments), total_patients, total_staff

    def _persist_patients(self):
        rows = [
            {"name": patient.name, "age": patient.age, "medical_record": patient.medical_record, "department": department.name}
            for department in self.hospital.departments
            for patient in department.patients
        ]
        self.patient_store.save_all(rows)

    def _persist_staff(self):
        rows = [
            {"name": staff_member.name, "age": staff_member.age, "position": staff_member.position, "department": department.name}
            for department in self.hospital.departments
            for staff_member in department.staff
        ]
        self.staff_store.save_all(rows)

    def _load_data(self):
        warnings = []

        for i, row in enumerate(self.patient_store.load(), start=2):
            try:
                department_name = row["department"]
                if department_name not in self.departments:
                    raise ValueError(f"unknown department '{department_name}'")
                patient = Patient(row["name"], int(row["age"]), row["medical_record"])
                self.departments[department_name].add_patient(patient)
            except (KeyError, ValueError, TypeError) as exc:
                warnings.append(f"patient_database.csv row {i}: {exc}")

        for i, row in enumerate(self.staff_store.load(), start=2):
            try:
                department_name = row["department"]
                if department_name not in self.departments:
                    raise ValueError(f"unknown department '{department_name}'")
                staff_member = Staff(row["name"], int(row["age"]), row["position"])
                self.departments[department_name].add_staff(staff_member)
            except (KeyError, ValueError, TypeError) as exc:
                warnings.append(f"staff_database.csv row {i}: {exc}")

        if warnings:
            messagebox.showwarning(
                "Some records were skipped",
                "The following rows could not be loaded and were skipped:\n\n" + "\n".join(warnings),
            )

    # ---------- sidebar ----------
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_row = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        logo_row.pack(fill="x", padx=24, pady=(30, 26))

        tk.Label(logo_row, text="✚", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_accent"], font=("Segoe UI", 22, "bold")).pack(side="left")
        title_box = tk.Frame(logo_row, bg=COLORS["sidebar_bg"])
        title_box.pack(side="left", padx=(10, 0))
        tk.Label(title_box, text="Hospital", bg=COLORS["sidebar_bg"], fg="white", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(title_box, text="Management System", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"], font=("Segoe UI", 8)).pack(anchor="w")

        nav_box = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        nav_box.pack(fill="x", pady=10)

        for name in NAV_ITEMS:
            row = tk.Frame(nav_box, bg=COLORS["sidebar_bg"])
            row.pack(fill="x")
            accent = tk.Frame(row, bg=COLORS["sidebar_bg"], width=3)
            accent.pack(side="left", fill="y")
            label = tk.Label(
                row, text=name, bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"],
                font=("Segoe UI", 11), anchor="w", padx=21, pady=12, cursor="hand2",
            )
            label.pack(side="left", fill="both", expand=True)
            label.bind("<Button-1>", lambda _e, n=name: self.show_page(n))
            label.bind("<Enter>", lambda _e, n=name: self._on_nav_hover(n, True))
            label.bind("<Leave>", lambda _e, n=name: self._on_nav_hover(n, False))
            self.nav_rows[name] = (accent, label)

        tk.Frame(sidebar, bg=COLORS["sidebar_hover"], height=1).pack(side="bottom", fill="x")
        info_box = tk.Frame(sidebar, bg=COLORS["sidebar_bg"])
        info_box.pack(side="bottom", fill="x", padx=24, pady=24)
        tk.Label(info_box, text="CURRENT HOSPITAL", bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(
            info_box, text=self.hospital.name, bg=COLORS["sidebar_bg"], fg="white",
            font=("Segoe UI", 11, "bold"), wraplength=190, justify="left",
        ).pack(anchor="w", pady=(4, 0))
        tk.Label(info_box, text=self.hospital.location, bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"], font=("Segoe UI", 9)).pack(anchor="w")

    def _on_nav_hover(self, name: str, entering: bool):
        if name == self.active_page:
            return
        _, label = self.nav_rows[name]
        label.configure(bg=COLORS["sidebar_hover"] if entering else COLORS["sidebar_bg"])

    def _refresh_nav_highlight(self):
        for name, (accent, label) in self.nav_rows.items():
            if name == self.active_page:
                accent.configure(bg=COLORS["sidebar_accent"])
                label.configure(bg=COLORS["sidebar_active"], fg=COLORS["sidebar_text_active"], font=("Segoe UI", 11, "bold"))
            else:
                accent.configure(bg=COLORS["sidebar_bg"])
                label.configure(bg=COLORS["sidebar_bg"], fg=COLORS["sidebar_text"], font=("Segoe UI", 11))

    # ---------- content shell ----------
    def _build_content_shell(self):
        content = ttkb.Frame(self)
        content.pack(side="left", fill="both", expand=True)

        top_bar = ttkb.Frame(content, padding=(24, 24, 24, 8))
        top_bar.pack(fill="x")

        self.page_title_var = tk.StringVar()
        ttkb.Label(top_bar, textvariable=self.page_title_var, font=FONT_TITLE).pack(side="left")
        ttkb.Label(top_bar, text="Hospital Administration", font=("Segoe UI", 10)).pack(side="right")

        self.page_container = ttkb.Frame(content, padding=(24, 0, 24, 24))
        self.page_container.pack(fill="both", expand=True)

    def show_page(self, name: str):
        self.active_page = name
        self.page_title_var.set(name)
        self._refresh_nav_highlight()

        for child in self.page_container.winfo_children():
            child.destroy()

        pages = {
            "Dashboard": DashboardPage,
            "Departments": DepartmentsPage,
            "Patients": PatientsPage,
            "Staff": StaffPage,
        }
        pages[name](self.page_container, self).pack(fill="both", expand=True)

    def refresh_current_page(self):
        self.show_page(self.active_page)

    # ---------- status bar ----------
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=COLORS["sidebar_bg"], height=32)
        bar.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="")
        tk.Label(
            bar, textvariable=self.status_var, bg=COLORS["sidebar_bg"], fg="white",
            font=("Segoe UI", 9), anchor="w", padx=16, pady=6,
        ).pack(fill="x")

    def set_status(self, message: str, duration_ms: int = 3000):
        if self._status_after_id is not None:
            self.after_cancel(self._status_after_id)
        self.status_var.set(message)
        self._status_after_id = self.after(duration_ms, lambda: self.status_var.set(""))


class DashboardPage(ttkb.Frame):
    def __init__(self, parent, app: HospitalApp):
        super().__init__(parent)
        self.app = app
        self._build_stats()
        self._build_breakdown()

    def _build_stats(self):
        stats_row = ttkb.Frame(self)
        stats_row.pack(fill="x", pady=(0, 16))

        dept_count, patient_count, staff_count = self.app.counts()
        values = {"Departments": dept_count, "Patients": patient_count, "Staff": staff_count}
        subtitles = {"Departments": "Active departments", "Patients": "Registered patients", "Staff": "Hospital employees"}

        for i, (title, letter, tint, accent) in enumerate(KPI_TOKENS):
            stats_row.columnconfigure(i, weight=1)
            outer, card = make_card(stats_row)
            outer.grid(row=0, column=i, sticky="nsew", padx=(0, 16) if i < 2 else 0)

            tk.Label(card, text=letter, bg=tint, fg=accent, font=("Segoe UI", 12, "bold"), width=2, height=1).pack(anchor="w")
            tk.Label(card, text=title, bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(12, 2))
            tk.Label(card, text=str(values[title]), bg=COLORS["card_bg"], fg=COLORS["text_primary"], font=FONT_KPI).pack(anchor="w")
            tk.Label(card, text=subtitles[title], bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=("Segoe UI", 9)).pack(anchor="w")

    def _build_breakdown(self):
        outer, card = make_card(self)
        outer.pack(fill="both", expand=True)

        tk.Label(card, text="Patients per Department", bg=COLORS["card_bg"], fg=COLORS["text_primary"], font=("Segoe UI", 14, "bold")).pack(
            anchor="w", pady=(0, 16)
        )

        counts = [(d.name, len(d.patients)) for d in self.app.hospital.departments]
        max_count = max((c for _, c in counts), default=0)

        for name, count in counts:
            row = tk.Frame(card, bg=COLORS["card_bg"])
            row.pack(fill="x", pady=6)

            tk.Label(row, text=name, bg=COLORS["card_bg"], fg=COLORS["text_primary"], font=("Segoe UI", 9), width=16, anchor="w").pack(side="left")

            track = tk.Frame(row, bg=COLORS["canvas"], height=10)
            track.pack(side="left", fill="x", expand=True, padx=8)
            track.pack_propagate(False)

            fraction = (count / max_count) if max_count else 0
            if fraction > 0:
                tk.Frame(track, bg=COLORS["primary"]).place(relx=0, rely=0, relwidth=fraction, relheight=1)

            tk.Label(row, text=str(count), bg=COLORS["card_bg"], fg=COLORS["text_primary"], font=("Segoe UI", 9, "bold"), width=3).pack(side="left")


class DepartmentsPage(ttkb.Frame):
    """Read-only: departments come only from Department.DEPARTMENTS, with
    live-computed patient/staff counts — nothing here is stored separately."""

    def __init__(self, parent, app: HospitalApp):
        super().__init__(parent)
        self.app = app

        columns = ("name", "patients", "staff")
        headings = {"name": "Department", "patients": "Patients", "staff": "Staff"}
        widths = {"name": 300, "patients": 140, "staff": 140}
        self.tree = make_table(self, columns, headings, widths)
        self._populate()

    def _populate(self):
        rows = [(d.name, len(d.patients), len(d.staff)) for d in self.app.hospital.departments]
        fill_table(self.tree, rows)


class PatientsPage(ttkb.Frame):
    def __init__(self, parent, app: HospitalApp):
        super().__init__(parent)
        self.app = app
        self._index: dict[str, tuple] = {}

        toolbar = ttkb.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))

        self.search_entry = ttkb.Entry(toolbar)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda _e: self._populate())

        self.delete_btn = ttkb.Button(toolbar, text="Delete", style="Danger.TButton", command=self._delete, state="disabled")
        self.delete_btn.pack(side="right", padx=(8, 0))
        self.edit_btn = ttkb.Button(toolbar, text="Edit", style="Secondary.TButton", command=self._edit, state="disabled")
        self.edit_btn.pack(side="right", padx=(8, 0))
        ttkb.Button(toolbar, text="+ Add", style="Primary.TButton", command=self._add).pack(side="right")

        self.status_label = ttkb.Label(self, text="", font=("Segoe UI", 9))
        self.status_label.pack(anchor="w", pady=(0, 8))

        columns = ("name", "age", "department", "record")
        headings = {"name": "Patient", "age": "Age", "department": "Department", "record": "Medical Record"}
        widths = {"name": 180, "age": 60, "department": 150, "record": 260}
        self.tree = make_table(self, columns, headings, widths)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._on_select())
        self.tree.bind("<Double-1>", lambda _e: self._edit())

        self._populate()

    def _all_patients(self):
        return [
            (patient, department.name)
            for department in self.app.hospital.departments
            for patient in department.patients
        ]

    def _populate(self):
        query = self.search_entry.get().strip().lower()
        all_rows = self._all_patients()
        shown = [(p, d) for (p, d) in all_rows if not query or query in p.name.lower() or query in d.lower()]

        self.tree.delete(*self.tree.get_children())
        self._index.clear()

        if not shown:
            message = f"No patient found matching '{query}'." if query else "No patients added yet — click + Add to get started."
            self.tree.insert("", "end", values=(message, "", "", ""), tags=("empty",))
        else:
            for i, (patient, department_name) in enumerate(shown):
                iid = self.tree.insert(
                    "", "end", values=(patient.name, patient.age, department_name, patient.medical_record),
                    tags=("odd",) if i % 2 else (),
                )
                self._index[iid] = (patient, department_name)

        self._on_select()

        if query and not shown:
            self.status_label.configure(text=f"✖  No patient found matching '{query}'.", foreground=COLORS["danger_text"])
        elif query:
            self.status_label.configure(text=f"✔  {len(shown)} patient(s) found.", foreground=COLORS["success_text"])
        else:
            self.status_label.configure(text=f"{len(all_rows)} registered patient(s).", foreground=COLORS["text_muted"])

    def _selected(self):
        selection = self.tree.selection()
        if not selection or selection[0] not in self._index:
            return None
        return self._index[selection[0]]

    def _on_select(self):
        state = "normal" if self._selected() is not None else "disabled"
        self.edit_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def _add(self):
        dialog = PatientDialog(self.app)
        self.wait_window(dialog)
        if dialog.result:
            self.app.add_patient(dialog.patient, dialog.department_name)
            self.app.set_status(f"Patient '{dialog.patient.name}' added.")
            self.app.refresh_current_page()

    def _edit(self):
        selected = self._selected()
        if not selected:
            return
        patient, department_name = selected
        dialog = PatientDialog(self.app, patient=patient, department_name=department_name)
        self.wait_window(dialog)
        if dialog.result:
            self.app.update_patient(patient, department_name, dialog.patient, dialog.department_name)
            self.app.set_status(f"Patient '{dialog.patient.name}' updated.")
            self.app.refresh_current_page()

    def _delete(self):
        selected = self._selected()
        if not selected:
            return
        patient, department_name = selected
        if not messagebox.askyesno("Confirm Delete", f"Delete patient '{patient.name}'?", parent=self):
            return
        self.app.delete_patient(patient, department_name)
        self.app.set_status(f"Patient '{patient.name}' deleted.")
        self.app.refresh_current_page()


class StaffPage(ttkb.Frame):
    def __init__(self, parent, app: HospitalApp):
        super().__init__(parent)
        self.app = app
        self._index: dict[str, tuple] = {}

        toolbar = ttkb.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))

        self.search_entry = ttkb.Entry(toolbar)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda _e: self._populate())

        self.delete_btn = ttkb.Button(toolbar, text="Delete", style="Danger.TButton", command=self._delete, state="disabled")
        self.delete_btn.pack(side="right", padx=(8, 0))
        self.edit_btn = ttkb.Button(toolbar, text="Edit", style="Secondary.TButton", command=self._edit, state="disabled")
        self.edit_btn.pack(side="right", padx=(8, 0))
        ttkb.Button(toolbar, text="+ Add", style="Primary.TButton", command=self._add).pack(side="right")

        self.status_label = ttkb.Label(self, text="", font=("Segoe UI", 9))
        self.status_label.pack(anchor="w", pady=(0, 8))

        columns = ("name", "age", "position", "department")
        headings = {"name": "Name", "age": "Age", "position": "Position", "department": "Department"}
        widths = {"name": 170, "age": 60, "position": 190, "department": 150}
        self.tree = make_table(self, columns, headings, widths)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._on_select())
        self.tree.bind("<Double-1>", lambda _e: self._edit())

        self._populate()

    def _all_staff(self):
        return [
            (staff_member, department.name)
            for department in self.app.hospital.departments
            for staff_member in department.staff
        ]

    def _populate(self):
        query = self.search_entry.get().strip().lower()
        all_rows = self._all_staff()
        shown = [(s, d) for (s, d) in all_rows if not query or query in s.name.lower() or query in d.lower()]

        self.tree.delete(*self.tree.get_children())
        self._index.clear()

        if not shown:
            message = f"No staff found matching '{query}'." if query else "No staff added yet — click + Add to get started."
            self.tree.insert("", "end", values=(message, "", "", ""), tags=("empty",))
        else:
            for i, (staff_member, department_name) in enumerate(shown):
                iid = self.tree.insert(
                    "", "end", values=(staff_member.name, staff_member.age, staff_member.position, department_name),
                    tags=("odd",) if i % 2 else (),
                )
                self._index[iid] = (staff_member, department_name)

        self._on_select()

        if query and not shown:
            self.status_label.configure(text=f"✖  No staff found matching '{query}'.", foreground=COLORS["danger_text"])
        elif query:
            self.status_label.configure(text=f"✔  {len(shown)} staff member(s) found.", foreground=COLORS["success_text"])
        else:
            self.status_label.configure(text=f"{len(all_rows)} staff member(s) on record.", foreground=COLORS["text_muted"])

    def _selected(self):
        selection = self.tree.selection()
        if not selection or selection[0] not in self._index:
            return None
        return self._index[selection[0]]

    def _on_select(self):
        state = "normal" if self._selected() is not None else "disabled"
        self.edit_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def _add(self):
        dialog = StaffDialog(self.app)
        self.wait_window(dialog)
        if dialog.result:
            self.app.add_staff(dialog.staff_member, dialog.department_name)
            self.app.set_status(f"Staff member '{dialog.staff_member.name}' added.")
            self.app.refresh_current_page()

    def _edit(self):
        selected = self._selected()
        if not selected:
            return
        staff_member, department_name = selected
        dialog = StaffDialog(self.app, staff_member=staff_member, department_name=department_name)
        self.wait_window(dialog)
        if dialog.result:
            self.app.update_staff(staff_member, department_name, dialog.staff_member, dialog.department_name)
            self.app.set_status(f"Staff member '{dialog.staff_member.name}' updated.")
            self.app.refresh_current_page()

    def _delete(self):
        selected = self._selected()
        if not selected:
            return
        staff_member, department_name = selected
        if not messagebox.askyesno("Confirm Delete", f"Delete staff member '{staff_member.name}'?", parent=self):
            return
        self.app.delete_staff(staff_member, department_name)
        self.app.set_status(f"Staff member '{staff_member.name}' deleted.")
        self.app.refresh_current_page()


if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
