
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from expenses_tab import ExpensesTab
from invoices_tab import InvoicesTab
from gallery_tab import GalleryTab
from timeline_tab import TimelineTab
from companies_tab import CompaniesTab
from database import create_connection, create_tables


class RenovationTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Renovation Expense Tracker")
        self.master.geometry("1024x768")
        self.master.minsize(1024, 768)

        self.company_colors = {}

        self.style = ttk.Style()
        self.style.configure('Equal.TButton', width=15)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        try:
            self.conn = create_connection()
            self.cursor = self.conn.cursor()
            create_tables(self.conn)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while setting up the database: {e}")
            self.master.destroy()
            return

        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.expenses_tab = ExpensesTab(self.notebook, self.conn, self.update_company_dropdowns)
        self.invoices_tab = InvoicesTab(self.notebook, self.conn)
        self.gallery_tab = GalleryTab(self.notebook, self.conn)
        self.timeline_tab = TimelineTab(self.notebook, self.conn, self.company_colors, self.update_company_dropdowns)
        self.companies_tab = CompaniesTab(self.notebook, self.conn, self.update_company_dropdowns)

        self.notebook.add(self.expenses_tab, text="Expenses")
        self.notebook.add(self.invoices_tab, text="Invoices")
        self.notebook.add(self.gallery_tab, text="Gallery")
        self.notebook.add(self.timeline_tab, text="Project Timeline")
        self.notebook.add(self.companies_tab, text="Companies")

    def update_company_dropdowns(self):
        try:
            self.cursor.execute("SELECT name, color FROM companies")
            companies = self.cursor.fetchall()
            self.expenses_tab.update_companies([row[0] for row in companies])
            self.timeline_tab.update_companies([row[0] for row in companies])
            self.company_colors = {row[0]: row[1] for row in companies}
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while updating company dropdowns: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenovationTracker(root)
    root.mainloop()















