# desktop_app/views/job_offer_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class JobOfferView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller

        # Crear un frame para esta vista
        self.job_offer_frame = ttk.Frame(self.parent)
        self.job_offer_frame.pack(fill="both", expand=True)

        # Crear el Treeview para mostrar las ofertas de empleo
        self.job_tree = ttk.Treeview(self.job_offer_frame, columns=("ID", "Title", "Company", "Location"), show="headings")
        self.job_tree.heading("ID", text="ID")
        self.job_tree.heading("Title", text="Título")
        self.job_tree.heading("Company", text="Empresa")
        self.job_tree.heading("Location", text="Ubicación")
        self.job_tree.pack(fill="both", expand=True)

        # Añadir un evento de selección en el Treeview
        self.job_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Frame para los campos de entrada
        input_frame = ttk.LabelFrame(self.job_offer_frame, text="Detalles de la Oferta")
        input_frame.pack(fill="x", padx=5, pady=5)

        # Campos de entrada para título, empresa y ubicación
        ttk.Label(input_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.title_entry = ttk.Entry(input_frame)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Empresa:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.company_entry = ttk.Entry(input_frame)
        self.company_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Ubicación:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.location_entry = ttk.Entry(input_frame)
        self.location_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Configurar el grid para que los campos se expandan
        input_frame.columnconfigure(1, weight=1)

        # Frame para los botones
        button_frame = ttk.Frame(self.job_offer_frame)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(button_frame, text="Añadir", command=self.add_job_offer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.update_job_offer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_job_offer).pack(side="left", padx=5)

        # Llamar al controlador para cargar las ofertas de empleo
        self.controller.load_job_offers()

    def on_tree_select(self, event):
        """Rellenar los campos de entrada cuando se selecciona una oferta en el Treeview."""
        selected_item = self.job_tree.selection()
        if selected_item:
            values = self.job_tree.item(selected_item, "values")
            # Limpiar los campos de entrada
            self.title_entry.delete(0, tk.END)
            self.company_entry.delete(0, tk.END)
            self.location_entry.delete(0, tk.END)
            # Rellenar los campos con los valores seleccionados
            self.title_entry.insert(0, values[1])  # Título
            self.company_entry.insert(0, values[2])  # Empresa
            self.location_entry.insert(0, values[3])  # Ubicación

    def add_job_offer(self):
        """Llamar al controlador para añadir una nueva oferta."""
        title = self.title_entry.get()
        company = self.company_entry.get()
        location = self.location_entry.get()

        if not title or not company:
            messagebox.showerror("Error", "El título y la empresa son obligatorios.")
            return

        try:
            self.controller.add_job_offer(title, company, location)
            # Limpiar los campos después de añadir
            self.title_entry.delete(0, tk.END)
            self.company_entry.delete(0, tk.END)
            self.location_entry.delete(0, tk.END)
            # Recargar las ofertas
            self.controller.load_job_offers()
            messagebox.showinfo("Éxito", "Oferta de empleo añadida correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir la oferta: {str(e)}")

    def update_job_offer(self):
        """Llamar al controlador para actualizar la oferta seleccionada."""
        selected_item = self.job_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una oferta para actualizar.")
            return

        offer_id = self.job_tree.item(selected_item, "values")[0]  # Obtener el ID de la oferta seleccionada
        title = self.title_entry.get()
        company = self.company_entry.get()
        location = self.location_entry.get()

        if not title or not company:
            messagebox.showerror("Error", "El título y la empresa son obligatorios.")
            return

        try:
            self.controller.update_job_offer(offer_id, title, company, location)
            # Recargar las ofertas
            self.controller.load_job_offers()
            messagebox.showinfo("Éxito", "Oferta de empleo actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la oferta: {str(e)}")

    def delete_job_offer(self):
        """Llamar al controlador para eliminar la oferta seleccionada."""
        selected_item = self.job_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una oferta para eliminar.")
            return

        offer_id = self.job_tree.item(selected_item, "values")[0]  # Obtener el ID de la oferta seleccionada

        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta oferta?"):
            try:
                self.controller.delete_job_offer(offer_id)
                # Recargar las ofertas
                self.controller.load_job_offers()
                messagebox.showinfo("Éxito", "Oferta de empleo eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la oferta: {str(e)}")