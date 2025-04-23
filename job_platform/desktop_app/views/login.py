"""
Vista de inicio de sesión para autenticación de usuarios.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.user import UserController
from ..utils import center_window, show_error_message, show_success_message
from ..styles import configure_styles

class LoginView(tk.Tk):
    """Ventana de inicio de sesión para autenticación de usuarios."""
    
    def __init__(self):
        """Inicializa la ventana de inicio de sesión."""
        super().__init__()
        
        self.title("Plataforma de Empleo - Inicio de Sesión")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Configurar estilos
        configure_styles()
        
        # Inicializar controlador
        self.user_controller = UserController()
        
        # Crear widgets
        self._create_widgets()
        
        # Centrar ventana
        center_window(self)
    
    def _create_widgets(self):
        """Crea y configura los widgets."""
        # Marco principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Inicio de Sesión",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Nombre de usuario
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Usuario:")
        username_label.pack(side=tk.LEFT)
        
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Contraseña
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = ttk.Label(password_frame, text="Contraseña:")
        password_label.pack(side=tk.LEFT)
        
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botón de inicio de sesión
        login_button = ttk.Button(
            main_frame,
            text="Iniciar Sesión",
            command=self._login
        )
        login_button.pack(pady=20)
        
        # Vincular tecla Enter al inicio de sesión
        self.bind('<Return>', lambda e: self._login())
    
    def _login(self):
        """Maneja el intento de inicio de sesión."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            show_error_message(self, "Por favor ingrese usuario y contraseña")
            return
        
        success, result = self.user_controller.authenticate_user(username, password)
        
        if success:
            show_success_message(self, "Inicio de sesión exitoso")
            self.destroy()  # Cerrar ventana de inicio de sesión
            # TODO: Abrir ventana principal de la aplicación
        else:
            show_error_message(self, result) 