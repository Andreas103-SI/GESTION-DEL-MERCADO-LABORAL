# desktop_app/views/user_view.py
import tkinter as tk
from tkinter import ttk

class UserView:
    def __init__(self, frame, controller):
        self.controller = controller
        self.frame = frame

        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(self.frame, text="Añadir/Editar Usuario")
        input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(input_frame, text="Nombre de usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.user_username_entry = ttk.Entry(input_frame)
        self.user_username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.user_email_entry = ttk.Entry(input_frame)
        self.user_email_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5)
        self.user_password_entry = ttk.Entry(input_frame, show="*")
        self.user_password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Rol:").grid(row=3, column=0, padx=5, pady=5)
        self.user_role_combo = ttk.Combobox(input_frame, values=["collaborator", "manager", "admin"])
        self.user_role_combo.grid(row=3, column=1, padx=5, pady=5)
        self.user_role_combo.set("collaborator")

        # Botones para CRUD
        ttk.Button(input_frame, text="Añadir", command=self.controller.add_user).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(input_frame, text="Actualizar", command=self.controller.update_user).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Eliminar", command=self.controller.delete_user).grid(row=4, column=2, padx=5, pady=5)

        # Tabla para mostrar usuarios
        self.user_tree = ttk.Treeview(self.frame, columns=("ID", "Username", "Email", "Rol"), show="headings")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("Rol", text="Rol")
        self.user_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.user_tree.bind("<<TreeviewSelect>>", self.controller.on_user_select)

        self.controller.load_users()