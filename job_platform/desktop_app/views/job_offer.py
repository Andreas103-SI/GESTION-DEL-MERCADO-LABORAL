"""
Vista para gestionar ofertas de trabajo.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ..controllers.job_offer import JobOfferController
from ..utils import (
    center_window, show_error_message, show_success_message,
    confirm_action, validate_date, format_date
)
from ..styles import configure_styles

class JobOfferView(ttk.Frame):
    """Vista para gestionar ofertas de trabajo."""
    
    def __init__(self, parent):
        """Inicializa la vista de ofertas de trabajo."""
        super().__init__(parent)
        
        # Inicializar controlador
        self.controller = JobOfferController()
        
        # Crear widgets
        self._create_widgets()
        
        # Cargar datos iniciales
        self._load_job_offers()
    
    def _create_widgets(self):
        """Crea y configura los widgets."""
        # Marco principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Ofertas de Trabajo",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Vista de árbol para ofertas de trabajo
        self.tree = ttk.Treeview(
            main_frame,
            columns=("id", "title", "company", "location", "publication_date"),
            show="headings"
        )
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Título")
        self.tree.heading("company", text="Empresa")
        self.tree.heading("location", text="Ubicación")
        self.tree.heading("publication_date", text="Fecha de Publicación")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=200)
        self.tree.column("company", width=150)
        self.tree.column("location", width=150)
        self.tree.column("publication_date", width=150)
        
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
            command=self._delete_job_offer
        )
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Botón Actualizar
        refresh_button = ttk.Button(
            buttons_frame,
            text="Actualizar",
            command=self._load_job_offers
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def _load_job_offers(self):
        """Carga las ofertas de trabajo en la vista de árbol."""
        # Limpiar elementos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener ofertas de trabajo
        success, result = self.controller.read()
        
        if success:
            for job_offer in result:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        job_offer.id,
                        job_offer.title,
                        job_offer.company,
                        job_offer.location,
                        format_date(job_offer.publication_date)
                    )
                )
        else:
            show_error_message(self, result)
    
    def _show_add_dialog(self):
        """Muestra el diálogo para agregar una nueva oferta de trabajo."""
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Oferta de Trabajo")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(form_frame, text="Título:")
        title_label.pack(fill=tk.X, pady=5)
        title_entry = ttk.Entry(form_frame)
        title_entry.pack(fill=tk.X, pady=5)
        
        # Empresa
        company_label = ttk.Label(form_frame, text="Empresa:")
        company_label.pack(fill=tk.X, pady=5)
        company_entry = ttk.Entry(form_frame)
        company_entry.pack(fill=tk.X, pady=5)
        
        # Ubicación
        location_label = ttk.Label(form_frame, text="Ubicación:")
        location_label.pack(fill=tk.X, pady=5)
        location_entry = ttk.Entry(form_frame)
        location_entry.pack(fill=tk.X, pady=5)
        
        # Fecha de Publicación
        date_label = ttk.Label(form_frame, text="Fecha de Publicación (YYYY-MM-DD):")
        date_label.pack(fill=tk.X, pady=5)
        date_entry = ttk.Entry(form_frame)
        date_entry.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda la nueva oferta de trabajo."""
            data = {
                "title": title_entry.get().strip(),
                "company": company_entry.get().strip(),
                "location": location_entry.get().strip(),
                "publication_date": date_entry.get().strip()
            }
            
            if not all(data.values()):
                show_error_message(dialog, "Todos los campos son requeridos")
                return
            
            if not validate_date(data["publication_date"]):
                show_error_message(dialog, "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            success, result = self.controller.create(data)
            
            if success:
                show_success_message(dialog, "Oferta de trabajo creada exitosamente")
                dialog.destroy()
                self._load_job_offers()
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
        """Muestra el diálogo para editar una oferta de trabajo."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione una oferta de trabajo para editar")
            return
        
        job_offer_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.read(job_offer_id)
        
        if not success:
            show_error_message(self, result)
            return
        
        job_offer = result
        
        dialog = tk.Toplevel(self)
        dialog.title("Editar Oferta de Trabajo")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Crear formulario
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(form_frame, text="Título:")
        title_label.pack(fill=tk.X, pady=5)
        title_entry = ttk.Entry(form_frame)
        title_entry.insert(0, job_offer.title)
        title_entry.pack(fill=tk.X, pady=5)
        
        # Empresa
        company_label = ttk.Label(form_frame, text="Empresa:")
        company_label.pack(fill=tk.X, pady=5)
        company_entry = ttk.Entry(form_frame)
        company_entry.insert(0, job_offer.company)
        company_entry.pack(fill=tk.X, pady=5)
        
        # Ubicación
        location_label = ttk.Label(form_frame, text="Ubicación:")
        location_label.pack(fill=tk.X, pady=5)
        location_entry = ttk.Entry(form_frame)
        location_entry.insert(0, job_offer.location)
        location_entry.pack(fill=tk.X, pady=5)
        
        # Fecha de Publicación
        date_label = ttk.Label(form_frame, text="Fecha de Publicación (YYYY-MM-DD):")
        date_label.pack(fill=tk.X, pady=5)
        date_entry = ttk.Entry(form_frame)
        date_entry.insert(0, format_date(job_offer.publication_date))
        date_entry.pack(fill=tk.X, pady=5)
        
        def save():
            """Guarda la oferta de trabajo editada."""
            data = {
                "title": title_entry.get().strip(),
                "company": company_entry.get().strip(),
                "location": location_entry.get().strip(),
                "publication_date": date_entry.get().strip()
            }
            
            if not all(data.values()):
                show_error_message(dialog, "Todos los campos son requeridos")
                return
            
            if not validate_date(data["publication_date"]):
                show_error_message(dialog, "Formato de fecha inválido. Use YYYY-MM-DD")
                return
            
            success, result = self.controller.update(job_offer_id, data)
            
            if success:
                show_success_message(dialog, "Oferta de trabajo actualizada exitosamente")
                dialog.destroy()
                self._load_job_offers()
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
    
    def _delete_job_offer(self):
        """Elimina la oferta de trabajo seleccionada."""
        selected = self.tree.selection()
        
        if not selected:
            show_error_message(self, "Por favor seleccione una oferta de trabajo para eliminar")
            return
        
        if not confirm_action(self, "¿Está seguro de que desea eliminar esta oferta de trabajo?"):
            return
        
        job_offer_id = self.tree.item(selected[0])["values"][0]
        success, result = self.controller.delete(job_offer_id)
        
        if success:
            show_success_message(self, result)
            self._load_job_offers()
        else:
            show_error_message(self, result) 