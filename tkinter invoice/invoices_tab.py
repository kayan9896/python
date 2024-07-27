
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class InvoicesTab(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left frame (form)
        left_frame = ttk.Frame(self, padding="10")
        left_frame.grid(row=0, column=0, sticky="ns")

        # Right frame (treeview)
        right_frame = ttk.Frame(self, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)

        # Invoice entry form (left frame)
        ttk.Label(left_frame, text="Invoice Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.invoice_number_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.invoice_number_var).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(left_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.invoice_amount_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.invoice_amount_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.invoice_amount_var.trace("w", lambda name, index, mode, sv=self.invoice_amount_var: self.calculate_hst(sv, self.invoice_hst_var))

        ttk.Label(left_frame, text="HST:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.invoice_hst_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.invoice_hst_var, state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(left_frame, text="Status:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.invoice_status_var = tk.StringVar()
        ttk.Combobox(left_frame, textvariable=self.invoice_status_var, 
                     values=["Pending", "Paid"]).grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Invoice", command=self.add_invoice, style='Equal.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Invoice", command=self.edit_invoice, style='Equal.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(left_frame, text="Delete Invoice", command=self.delete_invoice).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        # Invoice list (right frame)
        self.invoice_tree = ttk.Treeview(right_frame, columns=("ID", "Invoice Number", "Amount", "HST", "Status", "Date"), show="headings")
        self.invoice_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.invoice_tree.configure(yscroll=scrollbar.set)

        for col in self.invoice_tree['columns']:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=100)  # Adjust width as needed

        self.invoice_tree.bind("<ButtonRelease-1>", self.load_invoice_to_form)

        self.load_invoices()

    def calculate_hst(self, amount_var, hst_var):
        try:
            amount = float(amount_var.get())
            hst = amount * 0.13  # Assuming 13% HST
            hst_var.set(f"{hst:.2f}")
        except ValueError:
            hst_var.set("")

    def load_invoice_to_form(self, event):
        selected_item = self.invoice_tree.selection()
        if selected_item:
            values = self.invoice_tree.item(selected_item)['values']
            self.invoice_number_var.set(values[1])
            self.invoice_amount_var.set(values[2].replace('$', ''))
            self.invoice_hst_var.set(values[3].replace('$', ''))
            self.invoice_status_var.set(values[4])

    def add_invoice(self):
        try:
            invoice_number = self.invoice_number_var.get()
            amount = float(self.invoice_amount_var.get())
            hst = float(self.invoice_hst_var.get())
            status = self.invoice_status_var.get()
            date = datetime.now().strftime("%Y-%m-%d")

            self.cursor.execute("INSERT INTO invoices (invoice_number, amount, hst, status, date) VALUES (?, ?, ?, ?, ?)",
                                (invoice_number, amount, hst, status, date))
            self.conn.commit()
            self.load_invoices()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for Amount and HST.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while adding the invoice: {e}")

    def edit_invoice(self):
        selected_item = self.invoice_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an invoice to edit")
            return

        try:
            invoice_id = self.invoice_tree.item(selected_item)['values'][0]
            invoice_number = self.invoice_number_var.get()
            amount = float(self.invoice_amount_var.get())
            hst = float(self.invoice_hst_var.get())
            status = self.invoice_status_var.get()

            self.cursor.execute("UPDATE invoices SET invoice_number=?, amount=?, hst=?, status=? WHERE id=?",
                                (invoice_number, amount, hst, status, invoice_id))
            self.conn.commit()
            self.load_invoices()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for Amount and HST.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while editing the invoice: {e}")

    def delete_invoice(self):
        selected_item = self.invoice_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an invoice to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this invoice?"):
            try:
                invoice_id = self.invoice_tree.item(selected_item)['values'][0]
                self.cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
                self.conn.commit()
                self.load_invoices()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting the invoice: {e}")

    def load_invoices(self):
        self.invoice_tree.delete(*self.invoice_tree.get_children())
        try:
            self.cursor.execute("SELECT * FROM invoices")
            for row in self.cursor.fetchall():
                formatted_amount = f"${float(row[2]):.2f}"
                formatted_hst = f"${float(row[3]):.2f}"
                self.invoice_tree.insert("", "end", values=(row[0], row[1], formatted_amount, formatted_hst, row[4], row[5]))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading invoices: {e}")
