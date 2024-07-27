import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import sqlite3

class CompaniesTab(ttk.Frame):
    def __init__(self, parent, conn, update_callback):
        super().__init__(parent)
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.update_callback = update_callback
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Company Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_company_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.new_company_var).grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Add Company", command=self.add_company).grid(row=1, column=0, pady=10, padx=5, sticky="ew")
        ttk.Button(self, text="Edit Company", command=self.edit_company).grid(row=1, column=1, pady=10, padx=5, sticky="ew")
        ttk.Label(self, text="").grid(row=1, column=2, padx=10) # Spacer
        ttk.Button(self, text="Delete Company", command=self.delete_company).grid(row=1, column=3, pady=10, padx=5, sticky="ew")
        ttk.Label(self, text="").grid(row=1, column=4, padx=10) # Spacer
        ttk.Button(self, text="Change Color", command=self.change_company_color).grid(row=1, column=5, pady=10, padx=5, sticky="ew")

        self.company_listbox = tk.Listbox(self, width=50)
        self.company_listbox.grid(row=2, column=0, columnspan=6, padx=5, pady=5, sticky="nsew")
        
        self.load_companies_list()

    def add_company(self):
        company_name = self.new_company_var.get()
        if company_name:
            try:
                color = self.get_random_color()
                self.cursor.execute("INSERT INTO companies (name, color) VALUES (?, ?)", (company_name, color))
                self.conn.commit()
                self.load_companies_list()
                self.new_company_var.set("")
                self.update_callback()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Company name already exists")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while adding the company: {e}")

    def edit_company(self):
        selected_indices = self.company_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a company to edit")
            return

        old_name = self.company_listbox.get(selected_indices[0])
        new_name = simpledialog.askstring("Edit Company", "Enter new company name:", initialvalue=old_name)
        if new_name:
            try:
                self.cursor.execute("UPDATE companies SET name=? WHERE name=?", (new_name, old_name))
                self.conn.commit()
                self.load_companies_list()
                self.update_callback()  # Call the update callback
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Company name already exists")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while editing the company: {e}")

    def delete_company(self):
        selected_indices = self.company_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a company to delete")
            return

        company_name = self.company_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {company_name}?"):
            try:
                self.cursor.execute("DELETE FROM companies WHERE name=?", (company_name,))
                self.conn.commit()
                self.load_companies_list()
                self.update_callback()  # Call the update callback
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting the company: {e}")

    def change_company_color(self):
        selected_indices = self.company_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a company to change its color")
            return

        company_name = self.company_listbox.get(selected_indices[0])
        color = colorchooser.askcolor(title=f"Choose color for {company_name}")

        if color[1]:  # color is a tuple (RGB, hex)
            try:
                self.cursor.execute("UPDATE companies SET color=? WHERE name=?", (color[1], company_name))
                self.conn.commit()
                self.load_companies_list()
                self.update_callback()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while changing the company color: {e}")

    def get_random_color(self):
        import random
        return f'#{random.randint(0, 0xFFFFFF):06x}'

    def load_companies_list(self):
        self.company_listbox.delete(0, tk.END)
        try:
            self.cursor.execute("SELECT name, color FROM companies")
            for row in self.cursor.fetchall():
                self.company_listbox.insert(tk.END, row[0])
                self.company_listbox.itemconfigure(tk.END, {'bg': row[1]})
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading the companies list: {e}")
