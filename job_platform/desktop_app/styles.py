"""
Configuraciones de estilos globales para la aplicación de escritorio.
"""
import tkinter as tk
from tkinter import ttk

# Colores
PRIMARY_COLOR = "#4CAF50"  # Verde
SECONDARY_COLOR = "#2196F3"  # Azul
BACKGROUND_COLOR = "#f5f5f5"
TEXT_COLOR = "#333333"
ERROR_COLOR = "#f44336"

# Fuentes
FONT_FAMILY = "Arial"
FONT_SIZE_SMALL = 10
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14

def configure_styles():
    """Configura los estilos globales para la aplicación."""
    style = ttk.Style()
    
    # Configurar estilos de botones
    style.configure(
        "TButton",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background=PRIMARY_COLOR,
        foreground=TEXT_COLOR
    )
    
    # Configurar estilos de etiquetas
    style.configure(
        "TLabel",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background=BACKGROUND_COLOR,
        foreground=TEXT_COLOR
    )
    
    # Configurar estilos de campos de entrada
    style.configure(
        "TEntry",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        fieldbackground="white"
    )
    
    # Configurar estilos de marcos
    style.configure(
        "TFrame",
        background=BACKGROUND_COLOR
    )
    
    # Configurar estilos de vista de árbol
    style.configure(
        "Treeview",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
        background="white",
        fieldbackground="white"
    )
    
    style.configure(
        "Treeview.Heading",
        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
    )

def get_error_style():
    """Retorna la configuración de estilo para mensajes de error."""
    return {
        "font": (FONT_FAMILY, FONT_SIZE_SMALL),
        "foreground": ERROR_COLOR
    }

def get_success_style():
    """Retorna la configuración de estilo para mensajes de éxito."""
    return {
        "font": (FONT_FAMILY, FONT_SIZE_SMALL),
        "foreground": PRIMARY_COLOR
    } 