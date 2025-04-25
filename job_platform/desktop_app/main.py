# desktop_app/main.py
import os
import sys
import django
from django.conf import settings

# Configurar el entorno de Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')  # Ajusta 'job_platform' al nombre de tu proyecto
django.setup()

import tkinter as tk
from tkinter import ttk
from desktop_app.views.job_offer_view import JobOfferView
from desktop_app.views.task_view import TaskView
from desktop_app.views.user_view import UserView
from desktop_app.controllers.job_offer_controller import JobOfferController
from desktop_app.controllers.task_controller import TaskController
from desktop_app.controllers.user_controller import UserController  # Corregido: importamos UserController
from desktop_app.styles import configure_styles  # Importamos la función para aplicar estilos

class DesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Ofertas, Tareas y Usuarios")
        self.root.geometry("800x600")

        # Aplicar estilos globales
        configure_styles()

        # Configurar el fondo de la ventana principal
        self.root.configure(bg="#f5f5f5")  # Usamos BACKGROUND_COLOR definido en styles.py

        # Pestañas (Tabs) para gestionar diferentes modelos
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Pestaña para JobOffer
        self.job_offer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.job_offer_frame, text="Ofertas de Empleo")
        self.job_offer_controller = JobOfferController(self.job_offer_frame)
        self.job_offer_view = JobOfferView(self.job_offer_frame, self.job_offer_controller)
        self.job_offer_controller.set_view(self.job_offer_view)  # Conectamos la vista con el controlador

        # Pestaña para Task
        self.task_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_frame, text="Tareas")
        self.task_controller = TaskController(self.task_frame)
        self.task_view = TaskView(self.task_frame, self.task_controller)
        self.task_controller.set_view(self.task_view)  # Conectamos la vista con el controlador

        # Pestaña para CustomUser
        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text="Usuarios")
        self.user_controller = UserController(self.user_frame)
        self.user_view = UserView(self.user_frame, self.user_controller)
        self.user_controller.set_view(self.user_view)  # Conectamos la vista con el controlador

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopApp(root)
    root.mainloop()