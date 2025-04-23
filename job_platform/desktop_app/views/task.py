"""
Vista para gestionar tareas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.task import TaskController
from ..utils import (
    center_window, show_error_message, show_success_message,
    confirm_action, validate_date, format_date
)
from ..styles import configure_styles

class TaskView(ttk.Frame):
    """Vista para gestionar tareas."""
    
    def __init__(self, parent):
        """Inicializa la vista de tareas."""
        super().__init__(parent)
        
        # Inicializar controlador
        self.controller = TaskController()
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_tasks()
    
    def _create_widgets(self):
        """Crea y configura los widgets."""
        # Marco principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Tareas",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Vista de árbol para tareas
        self.tree = ttk.Treeview(
            main_frame,
            columns=("id", "title", "description", "status", "priority", "deadline", "project"),
            show="headings"
        )
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Título")
        self.tree.heading("description", text="Descripción")
        self.tree.heading("status", text="Estado")
        self.tree.heading("priority", text="Prioridad")
        self.tree.heading("deadline", text="Fecha Límite")
        self.tree.heading("project", text="Proyecto")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=150)
        self.tree.column("description", width=200)
        self.tree.column("status", width=100)
        self.tree.column("priority", width=100)
        self.tree.column("deadline", width=150)
        self.tree.column("project", width=150)
        
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
            command=self._delete_task
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Botón Actualizar
        refresh_button = ttk.Button(
            buttons_frame,
            text="Actualizar",
            command=self._load_tasks
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def _load_tasks(self):
        """Carga las tareas en la vista de árbol."""
        # Limpiar elementos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener tareas
        success, result = self.controller.read()
        
        if success:
            for task in result:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        task.id,
                        task.title,
                        task.description,
                        task.status,
                        task.priority,
                        format_date(task.deadline),
                        task.project
                    )
                )
        else:
            show_error_message(self, result)
    
    def _show_add_dialog(self):
        """Muestra el diálogo para agregar una nueva tarea."""
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Tarea")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(form_frame, text="Título:")
        title_label.pack(fill=tk.X, pady=5)
        title_entry = ttk.Entry(form_frame)
        title_entry.pack(fill=tk.X, pady=5)
        
        # Descripción
        description_label = ttk.Label(form_frame, text="Descripción:")
        description_label.pack(fill=tk.X, pady=5)
        description_entry = ttk.Entry(form_frame)
        description_entry.pack(fill=tk.X, pady=5)
        
        # Estado
        status_label = ttk.Label(form_frame, text="Estado:")
        status_label.pack(fill=tk.X, pady=5)
        status_combobox = ttk.Combobox(
            form_frame,
            values=["Pendiente", "En Progreso", "Completada"]
        )
        status_combobox.pack(fill=tk.X, pady=5)
        
        # Prioridad
        priority_label = ttk.Label(form_frame, text="Prioridad:")
        priority_label.pack(fill=tk.X, pady=5)
        priority_combobox = ttk.Combobox(
            form_frame,
            values=["Baja", "Media", "Alta"]
        )
        priority_combobox.pack(fill=tk.X, pady=5)
        
        # Fecha Límite
        deadline_label = ttk.Label(form_frame, text="Fecha Límite (YYYY-MM-DD):")
        deadline_label.pack(fill=tk.X, pady=5)
        deadline_entry = ttk.Entry(form_frame)
        deadline_entry.pack(fill=tk.X, pady=5)
        
        # Proyecto
        project_label = ttk.Label(form_frame, text="Proyecto:")
        project_label.pack(fill=tk.X, pady=5)
        project_entry = ttk.Entry(form_frame)
        project_entry.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda la nueva tarea."""
            data = {
                "title": title_entry.get().strip(),
                "description": description_entry.get().strip(),
                "status": status_combobox.get().strip(),
                "priority": priority_combobox.get().strip(),
                "deadline": deadline_entry.get().strip(),
                "project": project_entry.get().strip()
            }
            
            if not all(data.values()):
                show_error_message(dialog, "Todos los campos son requeridos")
                return
            
            if not validate_date(data["deadline"]):
                show_error_message(dialog, "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            success, result = self.controller.create(data)
            
            if success:
                show_success_message(dialog, "Tarea creada exitosamente")
                dialog.destroy()
                self._load_tasks()
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
        """Muestra el diálogo para editar una tarea."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione una tarea para editar")
            return
        
        task_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.read(task_id)
        
        if not success:
            show_error_message(self, result)
            return
        
        task = result
        
        dialog = tk.Toplevel(self)
        dialog.title("Editar Tarea")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(form_frame, text="Título:")
        title_label.pack(fill=tk.X, pady=5)
        title_entry = ttk.Entry(form_frame)
        title_entry.insert(0, task.title)
        title_entry.pack(fill=tk.X, pady=5)
        
        # Descripción
        description_label = ttk.Label(form_frame, text="Descripción:")
        description_label.pack(fill=tk.X, pady=5)
        description_entry = ttk.Entry(form_frame)
        description_entry.insert(0, task.description)
        description_entry.pack(fill=tk.X, pady=5)
        
        # Estado
        status_label = ttk.Label(form_frame, text="Estado:")
        status_label.pack(fill=tk.X, pady=5)
        status_combobox = ttk.Combobox(
            form_frame,
            values=["Pendiente", "En Progreso", "Completada"]
        )
        status_combobox.set(task.status)
        status_combobox.pack(fill=tk.X, pady=5)
        
        # Prioridad
        priority_label = ttk.Label(form_frame, text="Prioridad:")
        priority_label.pack(fill=tk.X, pady=5)
        priority_combobox = ttk.Combobox(
            form_frame,
            values=["Baja", "Media", "Alta"]
        )
        priority_combobox.set(task.priority)
        priority_combobox.pack(fill=tk.X, pady=5)
        
        # Fecha Límite
        deadline_label = ttk.Label(form_frame, text="Fecha Límite (YYYY-MM-DD):")
        deadline_label.pack(fill=tk.X, pady=5)
        deadline_entry = ttk.Entry(form_frame)
        deadline_entry.insert(0, format_date(task.deadline))
        deadline_entry.pack(fill=tk.X, pady=5)
        
        # Proyecto
        project_label = ttk.Label(form_frame, text="Proyecto:")
        project_label.pack(fill=tk.X, pady=5)
        project_entry = ttk.Entry(form_frame)
        project_entry.insert(0, task.project)
        project_entry.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda la tarea editada."""
            data = {
                "title": title_entry.get().strip(),
                "description": description_entry.get().strip(),
                "status": status_combobox.get().strip(),
                "priority": priority_combobox.get().strip(),
                "deadline": deadline_entry.get().strip(),
                "project": project_entry.get().strip()
            }
            
            if not all(data.values()):
                show_error_message(dialog, "Todos los campos son requeridos")
                return
            
            if not validate_date(data["deadline"]):
                show_error_message(dialog, "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            success, result = self.controller.update(task_id, data)
            
            if success:
                show_success_message(dialog, "Tarea actualizada exitosamente")
                dialog.destroy()
                self._load_tasks()
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
    
    def _delete_task(self):
        """Elimina la tarea seleccionada."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione una tarea para eliminar")
            return
        
        if not confirm_action(self, "¿Está seguro de que desea eliminar esta tarea?"):
            return
        
        task_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.delete(task_id)
        
        if success:
            show_success_message(self, result)
            self._load_tasks()
        else:
            show_error_message(self, result) 