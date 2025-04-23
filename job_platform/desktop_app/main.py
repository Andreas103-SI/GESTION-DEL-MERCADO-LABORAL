"""
Archivo principal de la aplicación de escritorio.
"""
import tkinter as tk
from tkinter import ttk
from .views.login import LoginView
from .views.job_offer import JobOfferView
from .views.task import TaskView
from .views.user import UserView
from .styles import configure_styles
from .utils import center_window

class MainApplication(tk.Tk):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la aplicación principal."""
        super().__init__()
        
        self.title("Plataforma de Empleo")
        self.geometry("800x600")
        
        # Configurar estilos
        configure_styles()
        
        # Crear vista de inicio de sesión
        self.login_view = LoginView()
        self.login_view.mainloop()
        
        # Crear ventana principal
        self._create_widgets()
        
        # Centrar ventana
        center_window(self)
    
    def _create_widgets(self):
        """Crea y configura los widgets."""
        # Marco principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Marco de navegación
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Botones de navegación
        job_offers_button = ttk.Button(
            nav_frame,
            text="Ofertas de Trabajo",
            command=lambda: self._show_view("job_offers")
        )
        job_offers_button.pack(fill=tk.X, pady=5)
        
        tasks_button = ttk.Button(
            nav_frame,
            text="Tareas",
            command=lambda: self._show_view("tasks")
        )
        tasks_button.pack(fill=tk.X, pady=5)
        
        users_button = ttk.Button(
            nav_frame,
            text="Usuarios",
            command=lambda: self._show_view("users")
        )
        users_button.pack(fill=tk.X, pady=5)
        
        # Marco de contenido
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicializar vistas
        self.views = {
            "job_offers": JobOfferView(self.content_frame),
            "tasks": TaskView(self.content_frame),
            "users": UserView(self.content_frame)
        }
        
        # Mostrar vista por defecto
        self._show_view("job_offers")
    
    def _show_view(self, view_name):
        """Muestra la vista especificada."""
        # Ocultar todas las vistas
        for view in self.views.values():
            view.pack_forget()
        
        # Mostrar vista seleccionada
        self.views[view_name].pack(fill=tk.BOTH, expand=True)

def main():
    """Punto de entrada principal de la aplicación."""
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    main() 