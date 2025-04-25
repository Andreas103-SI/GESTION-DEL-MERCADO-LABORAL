"""
Funciones de utilidad para la aplicación de escritorio.
"""
# desktop_app/utils.py
import tkinter as tk

def clear_job_entries(view):
    view.job_title_entry.delete(0, tk.END)
    view.job_company_entry.delete(0, tk.END)
    view.job_location_entry.delete(0, tk.END)
    view.job_source_entry.delete(0, tk.END)
    view.job_url_entry.delete(0, tk.END)

def clear_task_entries(view):
    view.task_title_entry.delete(0, tk.END)
    view.task_description_entry.delete(0, tk.END)
    view.task_state_combo.set("pending")
    view.task_priority_combo.set("medium")
    view.task_deadline_entry.delete(0, tk.END)
    view.task_project_entry.delete(0, tk.END)

def clear_user_entries(view):
    view.user_username_entry.delete(0, tk.END)
    view.user_email_entry.delete(0, tk.END)
    view.user_password_entry.delete(0, tk.END)
    view.user_role_combo.set("collaborator")