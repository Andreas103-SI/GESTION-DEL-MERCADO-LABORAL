# desktop_app/controllers/task_controller.py
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from projects.models import Task, Project
from desktop_app.utils import clear_task_entries
from desktop_app.styles import get_success_style, get_error_style

class TaskController:
    def __init__(self, frame):
        self.frame = frame
        self.view = None

    def set_view(self, view):
        self.view = view
        self.load_tasks()

    def load_tasks(self):
        for item in self.view.task_tree.get_children():
            self.view.task_tree.delete(item)
        for task in Task.objects.all():
            self.view.task_tree.insert("", "end", values=(task.id, task.title, task.state, task.priority, task.deadline, task.project.id))

    def add_task(self):
        title = self.view.task_title_entry.get()
        description = self.view.task_description_entry.get()
        state = self.view.task_state_combo.get()
        priority = self.view.task_priority_combo.get()
        deadline = self.view.task_deadline_entry.get()
        project_id = self.view.task_project_entry.get()

        if not all([title, description, state, priority, deadline, project_id]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            project = Project.objects.get(id=project_id)
            Task.objects.create(
                title=title,
                description=description,
                state=state,
                priority=priority,
                deadline=deadline_date,
                project=project
            )
            self.load_tasks()
            self.clear_task_entries()
            messagebox.showinfo("Éxito", "Tarea añadida correctamente", **get_success_style())
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido (use YYYY-MM-DD)", **get_error_style())
        except Project.DoesNotExist:
            messagebox.showerror("Error", "El proyecto no existe", **get_error_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir la tarea: {e}", **get_error_style())

    def update_task(self):
        selected_item = self.view.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una tarea para actualizar", **get_error_style())
            return

        task_id = self.view.task_tree.item(selected_item)["values"][0]
        title = self.view.task_title_entry.get()
        description = self.view.task_description_entry.get()
        state = self.view.task_state_combo.get()
        priority = self.view.task_priority_combo.get()
        deadline = self.view.task_deadline_entry.get()
        project_id = self.view.task_project_entry.get()

        if not all([title, description, state, priority, deadline, project_id]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            project = Project.objects.get(id=project_id)
            task = Task.objects.get(id=task_id)
            task.title = title
            task.description = description
            task.state = state
            task.priority = priority
            task.deadline = deadline_date
            task.project = project
            task.save()
            self.load_tasks()
            self.clear_task_entries()
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente", **get_success_style())
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido (use YYYY-MM-DD)", **get_error_style())
        except Project.DoesNotExist:
            messagebox.showerror("Error", "El proyecto no existe", **get_error_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tarea: {e}", **get_error_style())

    def delete_task(self):
        selected_item = self.view.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una tarea para eliminar", **get_error_style())
            return

        task_id = self.view.task_tree.item(selected_item)["values"][0]
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            self.load_tasks()
            self.clear_task_entries()
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la tarea: {e}", **get_error_style())

    def on_task_select(self, event):
        selected_item = self.view.task_tree.selection()
        if selected_item:
            values = self.view.task_tree.item(selected_item)["values"]
            self.view.task_title_entry.delete(0, tk.END)
            self.view.task_title_entry.insert(0, values[1])
            self.view.task_description_entry.delete(0, tk.END)
            self.view.task_description_entry.insert(0, Task.objects.get(id=values[0]).description)
            self.view.task_state_combo.set(values[2])
            self.view.task_priority_combo.set(values[3])
            self.view.task_deadline_entry.delete(0, tk.END)
            self.view.task_deadline_entry.insert(0, values[4])
            self.view.task_project_entry.delete(0, tk.END)
            self.view.task_project_entry.insert(0, values[5])

    def clear_task_entries(self):
        clear_task_entries(self.view)