import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ExpensesTab(ttk.Frame):
    def __init__(self, parent, conn, update_callback):
        super().__init__(parent)
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.update_callback = update_callback
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

        # Expense entry form (left frame)
        ttk.Label(left_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        ttk.Combobox(left_frame, textvariable=self.category_var, 
                     values=["Plumbing", "Electrical", "Construction", "General"]).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(left_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.amount_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.amount_var.trace("w", lambda name, index, mode, sv=self.amount_var: self.calculate_hst(sv, self.hst_var))

        ttk.Label(left_frame, text="HST:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.hst_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.hst_var, state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(left_frame, text="Company:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.company_var = tk.StringVar()
        self.company_combobox = ttk.Combobox(left_frame, textvariable=self.company_var)
        self.company_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.load_companies()

        ttk.Label(left_frame, text="Description:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.description_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.description_var).grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Expense", command=self.add_expense, style='Equal.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Expense", command=self.edit_expense, style='Equal.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Button(left_frame, text="Delete Expense", command=self.delete_expense).grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

        # Expense list (right frame)
        self.expense_tree = ttk.Treeview(right_frame, columns=("ID", "Category", "Amount", "HST", "Company", "Description", "Date"), show="headings")
        self.expense_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.expense_tree.configure(yscroll=scrollbar.set)

        for col in self.expense_tree['columns']:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=100)  # Adjust width as needed

        self.expense_tree.bind("<ButtonRelease-1>", self.load_expense_to_form)

        self.load_expenses()

    def calculate_hst(self, amount_var, hst_var):
        try:
            amount = float(amount_var.get())
            hst = amount * 0.13  # Assuming 13% HST
            hst_var.set(f"{hst:.2f}")
        except ValueError:
            hst_var.set("")

    def load_companies(self):
        self.cursor.execute("SELECT name FROM companies")
        companies = [row[0] for row in self.cursor.fetchall()]
        self.company_combobox['values'] = companies

    def update_companies(self, companies):
        self.company_combobox['values'] = companies

    def load_expense_to_form(self, event):
        selected_item = self.expense_tree.selection()
        if selected_item:
            values = self.expense_tree.item(selected_item)['values']
            self.category_var.set(values[1])
            self.amount_var.set(values[2].replace('$', ''))
            self.hst_var.set(values[3].replace('$', ''))
            self.company_var.set(values[4])
            self.description_var.set(values[5])

    def add_expense(self):
        try:
            category = self.category_var.get()
            amount = float(self.amount_var.get())
            hst = float(self.hst_var.get())
            company = self.company_var.get()
            description = self.description_var.get()
            date = datetime.now().strftime("%Y-%m-%d")

            self.cursor.execute("INSERT INTO expenses (category, amount, hst, company, description, date) VALUES (?, ?, ?, ?, ?, ?)",
                                (category, amount, hst, company, description, date))
            self.conn.commit()
            self.load_expenses()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for Amount and HST.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while adding the expense: {e}")

    def edit_expense(self):
        selected_item = self.expense_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an expense to edit")
            return

        try:
            expense_id = self.expense_tree.item(selected_item)['values'][0]
            category = self.category_var.get()
            amount = float(self.amount_var.get())
            hst = float(self.hst_var.get())
            company = self.company_var.get()
            description = self.description_var.get()

            self.cursor.execute("UPDATE expenses SET category=?, amount=?, hst=?, company=?, description=? WHERE id=?",
                                (category, amount, hst, company, description, expense_id))
            self.conn.commit()
            self.load_expenses()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for Amount and HST.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while editing the expense: {e}")

    def delete_expense(self):
        selected_item = self.expense_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an expense to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            try:
                expense_id = self.expense_tree.item(selected_item)['values'][0]
                self.cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
                self.conn.commit()
                self.load_expenses()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting the expense: {e}")

    def load_expenses(self):
        self.expense_tree.delete(*self.expense_tree.get_children())
        try:
            self.cursor.execute("SELECT * FROM expenses")
            for row in self.cursor.fetchall():
                formatted_amount = f"${float(row[2]):.2f}"
                formatted_hst = f"${float(row[3]):.2f}"
                self.expense_tree.insert("", "end", values=(row[0], row[1], formatted_amount, formatted_hst, row[4], row[5], row[6]))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading expenses: {e}")
