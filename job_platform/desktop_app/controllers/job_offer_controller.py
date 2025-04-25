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

    def load_job_offers(self):
        for item in self.view.job_tree.get_children():
            self.view.job_tree.delete(item)
        for job in JobOffer.objects.all():
            self.view.job_tree.insert("", "end", values=(job.id, job.title, job.company, job.location, job.source, job.url))

    def add_job_offer(self):
        title = self.view.job_title_entry.get()
        company = self.view.job_company_entry.get()
        location = self.view.job_location_entry.get()
        source = self.view.job_source_entry.get()
        url = self.view.job_url_entry.get()
        publication_date = datetime.now().date()

        if not all([title, company, location, source, url]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            JobOffer.objects.create(
                title=title,
                company=company,
                location=location,
                source=source,
                url=url,
                publication_date=publication_date
            )
            self.load_job_offers()
            self.clear_job_entries()
            messagebox.showinfo("Éxito", "Oferta añadida correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir la oferta: {e}", **get_error_style())

    def update_job_offer(self):
        selected_item = self.view.job_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una oferta para actualizar", **get_error_style())
            return

        job_id = self.view.job_tree.item(selected_item)["values"][0]
        title = self.view.job_title_entry.get()
        company = self.view.job_company_entry.get()
        location = self.view.job_location_entry.get()
        source = self.view.job_source_entry.get()
        url = self.view.job_url_entry.get()

        if not all([title, company, location, source, url]):
            messagebox.showerror("Error", "Todos los campos son obligatorios", **get_error_style())
            return

        try:
            job = JobOffer.objects.get(id=job_id)
            job.title = title
            job.company = company
            job.location = location
            job.source = source
            job.url = url
            job.save()
            self.load_job_offers()
            self.clear_job_entries()
            messagebox.showinfo("Éxito", "Oferta actualizada correctamente", **get_success_style())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la oferta: {e}", **get_error_style())

    def delete_job_offer(self):
        selected_item = self.view.job_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona una oferta para eliminar", **get_error_style())
            return

        job_id = self.view.job_tree.item(selected_item)["values"][0]
        try:
            job = JobOffer.objects.get(id=job_id)
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
            self.view.job_title_entry.delete(0, tk.END)
            self.view.job_title_entry.insert(0, values[1])
            self.view.job_company_entry.delete(0, tk.END)
            self.view.job_company_entry.insert(0, values[2])
            self.view.job_location_entry.delete(0, tk.END)
            self.view.job_location_entry.insert(0, values[3])
            self.view.job_source_entry.delete(0, tk.END)
            self.view.job_source_entry.insert(0, values[4])
            self.view.job_url_entry.delete(0, tk.END)
            self.view.job_url_entry.insert(0, values[5])

    def clear_job_entries(self):
        clear_job_entries(self.view)