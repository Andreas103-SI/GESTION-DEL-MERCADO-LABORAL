"""
Funciones de utilidad para la aplicación de escritorio.
"""
import tkinter as tk
from datetime import datetime
import re

def center_window(window):
    """Centra una ventana en la pantalla."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def validate_date(date_str):
    """Valida el formato de fecha (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_email(email):
    """Valida el formato de correo electrónico."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_required_fields(fields):
    """Valida que todos los campos requeridos estén llenos."""
    return all(field.get().strip() for field in fields)

def show_error_message(parent, message):
    """Muestra un mensaje de error en una ventana emergente."""
    tk.messagebox.showerror("Error", message, parent=parent)

def show_success_message(parent, message):
    """Muestra un mensaje de éxito en una ventana emergente."""
    tk.messagebox.showinfo("Éxito", message, parent=parent)

def confirm_action(parent, message):
    """Muestra un diálogo de confirmación."""
    return tk.messagebox.askyesno("Confirmar", message, parent=parent)

def format_date(date):
    """Formatea un objeto de fecha a cadena YYYY-MM-DD."""
    return date.strftime('%Y-%m-%d') if date else ''

def parse_date(date_str):
    """Convierte una cadena YYYY-MM-DD a un objeto de fecha."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None 