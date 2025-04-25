# desktop_app/controllers/job_offer_controller.py
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from market_analysis.models import JobOffer
from desktop_app.utils import clear_job_entries
from desktop_app.styles import get_success_style, get_error_style

class JobOfferController:
    def __init__(self, frame):
        self.frame = frame
        self.view = None

    def set_view(self, view):
        self.view = view
        self.load_job_offers()  # Cargar las ofertas después de asignar la vista

    def load_job_offers(self):
        for item in self.view.job_tree.get_children():
            self.view.job_tree.delete(item)
        for job in JobOffer.objects.all():
            self.view.job_tree.insert("", "end", values=(job.id, job.title, job.company, job.location))

    def add_job_offer(self, title, company, location):
        if not all([title, company, location]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            JobOffer.objects.create(
                title=title,
                company=company,
                location=location,
                publication_date=datetime.now().date()
            )
            self.load_job_offers()
            self.clear_job_entries()
            messagebox.showinfo("Éxito", "Oferta añadida correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir la oferta: {e}", **get_error_style())

    def update_job_offer(self, offer_id, title, company, location):
        try:
            job = JobOffer.objects.get(id=offer_id)
            job.title = title
            job.company = company
            job.location = location
            job.save()
            self.load_job_offers()
            self.clear_job_entries()
            messagebox.showinfo("Éxito", "Oferta actualizada correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la oferta: {e}", **get_error_style())

    def delete_job_offer(self, offer_id):
        try:
            job = JobOffer.objects.get(id=offer_id)
            job.delete()
            self.load_job_offers()
            self.clear_job_entries()
            messagebox.showinfo("Éxito", "Oferta eliminada correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la oferta: {e}", **get_error_style())

    def on_job_select(self, event):
        selected_item = self.view.job_tree.selection()
        if selected_item:
            values = self.view.job_tree.item(selected_item)["values"]
            self.view.title_entry.delete(0, tk.END)
            self.view.title_entry.insert(0, values[1])
            self.view.company_entry.delete(0, tk.END)
            self.view.company_entry.insert(0, values[2])
            self.view.location_entry.delete(0, tk.END)
            self.view.location_entry.insert(0, values[3])

    def clear_job_entries(self):
        clear_job_entries(self.view)