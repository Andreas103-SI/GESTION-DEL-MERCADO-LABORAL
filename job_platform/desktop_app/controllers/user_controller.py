# desktop_app/controllers/user_controller.py
import tkinter as tk
from tkinter import messagebox
from users.models import CustomUser
from desktop_app.utils import clear_user_entries
from desktop_app.styles import get_success_style, get_error_style

class UserController:
    def __init__(self, frame):
        self.frame = frame
        self.view = None

    def set_view(self, view):
        self.view = view
        self.load_users()

    def load_users(self):
        for item in self.view.user_tree.get_children():
            self.view.user_tree.delete(item)
        for user in CustomUser.objects.all():
            self.view.user_tree.insert("", "end", values=(user.id, user.username, user.email, user.role))

    def add_user(self):
        username = self.view.user_username_entry.get()
        email = self.view.user_email_entry.get()
        password = self.view.user_password_entry.get()
        role = self.view.user_role_combo.get()

        if not all([username, email, password, role]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            self.load_users()
            self.clear_user_entries()
            messagebox.showinfo("Éxito", "Usuario añadido correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir el usuario: {e}", **get_error_style())

    def update_user(self):
        selected_item = self.view.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un usuario para actualizar", **get_error_style())
            return

        user_id = self.view.user_tree.item(selected_item)["values"][0]
        username = self.view.user_username_entry.get()
        email = self.view.user_email_entry.get()
        password = self.view.user_password_entry.get()
        role = self.view.user_role_combo.get()

        if not all([username, email, role]):
            messagebox.showerror("Error", "Todos los campos (excepto contraseña) son obligatorios", **get_error_style())
            return

        try:
            user = CustomUser.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.role = role
            if password:  # Solo actualizar contraseña si se proporciona
                user.set_password(password)
            user.save()
            self.load_users()
            self.clear_user_entries()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el usuario: {e}", **get_error_style())

    def delete_user(self):
        selected_item = self.view.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un usuario para eliminar", **get_error_style())
            return

        user_id = self.view.user_tree.item(selected_item)["values"][0]
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            self.load_users()
            self.clear_user_entries()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {e}", **get_error_style())

    def on_user_select(self, event):
        selected_item = self.view.user_tree.selection()
        if selected_item:
            values = self.view.user_tree.item(selected_item)["values"]
            self.view.user_username_entry.delete(0, tk.END)
            self.view.user_username_entry.insert(0, values[1])
            self.view.user_email_entry.delete(0, tk.END)
            self.view.user_email_entry.insert(0, values[2])
            self.view.user_password_entry.delete(0, tk.END)
            self.view.user_role_combo.set(values[3])

    def clear_user_entries(self):
        clear_user_entries(self.view)