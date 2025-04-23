"""
Vista para gestionar usuarios.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.user import UserController
from ..utils import (
    center_window, show_error_message, show_success_message,
    confirm_action, validate_email
)
from ..styles import configure_styles

class UserView(ttk.Frame):
    """Vista para gestionar usuarios."""
    
    def __init__(self, parent):
        """Inicializa la vista de usuarios."""
        super().__init__(parent)
        
        # Inicializar controlador
        self.controller = UserController()
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_users()
    
    def _create_widgets(self):
        """Crea y configura los widgets."""
        # Marco principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Usuarios",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Vista de árbol para usuarios
        self.tree = ttk.Treeview(
            main_frame,
            columns=("id", "username", "email", "is_active"),
            show="headings"
        )
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Usuario")
        self.tree.heading("email", text="Correo Electrónico")
        self.tree.heading("is_active", text="Activo")
        
        self.tree.column("id", width=50)
        self.tree.column("username", width=150)
        self.tree.column("email", width=200)
        self.tree.column("is_active", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Marco de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botón Agregar
        add_button = ttk.Button(
            buttons_frame,
            text="Agregar",
            command=self._show_add_dialog
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Botón Editar
        edit_button = ttk.Button(
            buttons_frame,
            text="Editar",
            command=self._show_edit_dialog
        )
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # Botón Eliminar
        delete_button = ttk.Button(
            buttons_frame,
            text="Eliminar",
            command=self._delete_user
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Botón Actualizar
        refresh_button = ttk.Button(
            buttons_frame,
            text="Actualizar",
            command=self._load_users
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def _load_users(self):
        """Carga los usuarios en la vista de árbol."""
        # Limpiar elementos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener usuarios
        success, result = self.controller.read()
        
        if success:
            for user in result:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        user.id,
                        user.username,
                        user.email,
                        "Sí" if user.is_active else "No"
                    )
                )
        else:
            show_error_message(self, result)
    
    def _show_add_dialog(self):
        """Muestra el diálogo para agregar un nuevo usuario."""
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Usuario")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Usuario
        username_label = ttk.Label(form_frame, text="Usuario:")
        username_label.pack(fill=tk.X, pady=5)
        username_entry = ttk.Entry(form_frame)
        username_entry.pack(fill=tk.X, pady=5)
        
        # Correo Electrónico
        email_label = ttk.Label(form_frame, text="Correo Electrónico:")
        email_label.pack(fill=tk.X, pady=5)
        email_entry = ttk.Entry(form_frame)
        email_entry.pack(fill=tk.X, pady=5)
        
        # Contraseña
        password_label = ttk.Label(form_frame, text="Contraseña:")
        password_label.pack(fill=tk.X, pady=5)
        password_entry = ttk.Entry(form_frame, show="*")
        password_entry.pack(fill=tk.X, pady=5)
        
        # Activo
        is_active_var = tk.BooleanVar(value=True)
        is_active_check = ttk.Checkbutton(
            form_frame,
            text="Activo",
            variable=is_active_var
        )
        is_active_check.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda el nuevo usuario."""
            data = {
                "username": username_entry.get().strip(),
                "email": email_entry.get().strip(),
                "password": password_entry.get(),
                "is_active": is_active_var.get()
            }
            
            if not all([data["username"], data["email"], data["password"]]):
                show_error_message(dialog, "Todos los campos son requeridos")
                return
            
            if not validate_email(data["email"]):
                show_error_message(dialog, "Formato de correo electrónico inválido")
                return
            
            success, result = self.controller.create(data)
            
            if success:
                show_success_message(dialog, "Usuario creado exitosamente")
                dialog.destroy()
                self._load_users()
            else:
                show_error_message(dialog, result)
        
        # Botón Guardar
        save_button = ttk.Button(
            form_frame,
            text="Guardar",
            command=save
        )
        save_button.pack(pady=20)
        
        # Centrar diálogo
        center_window(dialog)
    
    def _show_edit_dialog(self):
        """Muestra el diálogo para editar un usuario."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione un usuario para editar")
            return
        
        user_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.read(user_id)
        
        if not success:
            show_error_message(self, result)
            return
        
        user = result
        
        dialog = tk.Toplevel(self)
        dialog.title("Editar Usuario")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Usuario
        username_label = ttk.Label(form_frame, text="Usuario:")
        username_label.pack(fill=tk.X, pady=5)
        username_entry = ttk.Entry(form_frame)
        username_entry.insert(0, user.username)
        username_entry.pack(fill=tk.X, pady=5)
        
        # Correo Electrónico
        email_label = ttk.Label(form_frame, text="Correo Electrónico:")
        email_label.pack(fill=tk.X, pady=5)
        email_entry = ttk.Entry(form_frame)
        email_entry.insert(0, user.email)
        email_entry.pack(fill=tk.X, pady=5)
        
        # Contraseña
        password_label = ttk.Label(form_frame, text="Nueva Contraseña (dejar en blanco para mantener la actual):")
        password_label.pack(fill=tk.X, pady=5)
        password_entry = ttk.Entry(form_frame, show="*")
        password_entry.pack(fill=tk.X, pady=5)
        
        # Activo
        is_active_var = tk.BooleanVar(value=user.is_active)
        is_active_check = ttk.Checkbutton(
            form_frame,
            text="Activo",
            variable=is_active_var
        )
        is_active_check.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda el usuario editado."""
            data = {
                "username": username_entry.get().strip(),
                "email": email_entry.get().strip(),
                "is_active": is_active_var.get()
            }
            
            if not all([data["username"], data["email"]]):
                show_error_message(dialog, "Usuario y correo electrónico son requeridos")
                return
            
            if not validate_email(data["email"]):
                show_error_message(dialog, "Formato de correo electrónico inválido")
                return
            
            # Solo incluir contraseña si no está vacía
            password = password_entry.get()
            if password:
                data["password"] = password
            
            success, result = self.controller.update(user_id, data)
            
            if success:
                show_success_message(dialog, "Usuario actualizado exitosamente")
                dialog.destroy()
                self._load_users()
            else:
                show_error_message(dialog, result)
        
        # Botón Guardar
        save_button = ttk.Button(
            form_frame,
            text="Guardar",
            command=save
        )
        save_button.pack(pady=20)
        
        # Centrar diálogo
        center_window(dialog)
    
    def _delete_user(self):
        """Elimina el usuario seleccionado."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione un usuario para eliminar")
            return
        
        if not confirm_action(self, "¿Está seguro de que desea eliminar este usuario?"):
            return
        
        user_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.delete(user_id)
        
        if success:
            show_success_message(self, result)
            self._load_users()
        else:
            show_error_message(self, result) 