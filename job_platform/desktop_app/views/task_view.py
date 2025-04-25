# desktop_app/views/task_view.py
import tkinter as tk
from tkinter import ttk

class TaskView:
    def __init__(self, frame, controller):
        self.controller = controller
        self.frame = frame

        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(self.frame, text="Añadir/Editar Tarea")
        input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(input_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5)
        self.task_title_entry = ttk.Entry(input_frame)
        self.task_title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
        self.task_description_entry = ttk.Entry(input_frame)
        self.task_description_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Estado:").grid(row=2, column=0, padx=5, pady=5)
        self.task_state_combo = ttk.Combobox(input_frame, values=["pending", "in_progress", "completed"])
        self.task_state_combo.grid(row=2, column=1, padx=5, pady=5)
        self.task_state_combo.set("pending")

        ttk.Label(input_frame, text="Prioridad:").grid(row=3, column=0, padx=5, pady=5)
        self.task_priority_combo = ttk.Combobox(input_frame, values=["low", "medium", "high"])
        self.task_priority_combo.grid(row=3, column=1, padx=5, pady=5)
        self.task_priority_combo.set("medium")

        ttk.Label(input_frame, text="Fecha límite (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5)
        self.task_deadline_entry = ttk.Entry(input_frame)
        self.task_deadline_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Proyecto (ID):").grid(row=5, column=0, padx=5, pady=5)
        self.task_project_entry = ttk.Entry(input_frame)
        self.task_project_entry.grid(row=5, column=1, padx=5, pady=5)

        # Botones para CRUD
        ttk.Button(input_frame, text="Añadir", command=self.controller.add_task).grid(row=6, column=0, padx=5, pady=5)
        ttk.Button(input_frame, text="Actualizar", command=self.controller.update_task).grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Eliminar", command=self.controller.delete_task).grid(row=6, column=2, padx=5, pady=5)

        # Tabla para mostrar tareas
        self.task_tree = ttk.Treeview(self.frame, columns=("ID", "Título", "Estado", "Prioridad", "Fecha límite", "Proyecto"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Título", text="Título")
        self.task_tree.heading("Estado", text="Estado")
        self.task_tree.heading("Prioridad", text="Prioridad")
        self.task_tree.heading("Fecha límite", text="Fecha límite")
        self.task_tree.heading("Proyecto", text="Proyecto")
        self.task_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.task_tree.bind("<<TreeviewSelect>>", self.controller.on_task_select)

        self.controller.load_tasks()