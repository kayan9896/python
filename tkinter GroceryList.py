import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class GroceryListApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Grocery List App')
        self.grocery_list = {}

        # Create frames
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(padx=10, pady=10)

        self.list_frame = ttk.Frame(self.root)
        self.list_frame.pack(padx=10, pady=10)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(padx=10, pady=10)

        # Create input fields
        self.item_label = ttk.Label(self.input_frame, text='Item:')
        self.item_label.pack(side=tk.LEFT)

        self.item_entry = ttk.Entry(self.input_frame, width=20)
        self.item_entry.pack(side=tk.LEFT)

        self.category_label = ttk.Label(self.input_frame, text='Category:')
        self.category_label.pack(side=tk.LEFT)

        self.category_entry = ttk.Entry(self.input_frame, width=20)
        self.category_entry.pack(side=tk.LEFT)

        self.quantity_label = ttk.Label(self.input_frame, text='Quantity:')
        self.quantity_label.pack(side=tk.LEFT)

        self.quantity_entry = ttk.Entry(self.input_frame, width=5)
        self.quantity_entry.pack(side=tk.LEFT)

        # Create buttons
        self.add_button = ttk.Button(self.input_frame, text='Add', command=self.add_item)
        self.add_button.pack(side=tk.LEFT)

        self.remove_button = ttk.Button(self.input_frame, text='Remove', command=self.remove_item)
        self.remove_button.pack(side=tk.LEFT)

        # Create list box
        self.list_box = tk.Listbox(self.list_frame, width=50)
        self.list_box.pack(padx=10, pady=10)

        # Create export and import buttons
        self.export_button = ttk.Button(self.button_frame, text='Export List', command=self.export_list)
        self.export_button.pack(side=tk.LEFT)

        self.import_button = ttk.Button(self.button_frame, text='Import List', command=self.import_list)
        self.import_button.pack(side=tk.LEFT)

        self.edit_button = ttk.Button(self.button_frame, text='Edit Item', command=self.edit_item)
        self.edit_button.pack(side=tk.LEFT)

    def add_item(self):
        item = self.item_entry.get()
        category = self.category_entry.get()
        quantity = self.quantity_entry.get()

        if item and category and quantity:
            self.grocery_list[item] = {'category': category, 'quantity': quantity}
            self.list_box.insert(tk.END, f'{item} - {category} - {quantity}')
            self.item_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
        else:
            messagebox.showerror('Error', 'Please fill out all fields')

    def remove_item(self):
        try:
            selected_index = self.list_box.curselection()[0]
            item = self.list_box.get(selected_index).split(' - ')[0]
            del self.grocery_list[item]
            self.list_box.delete(selected_index)
        except IndexError:
            messagebox.showerror('Error', 'Please select an item to remove')

    def export_list(self):
        file_name = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(self.grocery_list, file)

    def import_list(self):
        file_name = filedialog.askopenfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')])
        if file_name:
            with open(file_name, 'r') as file:
                self.grocery_list = json.load(file)
                self.list_box.delete(0, tk.END)
                for item, values in self.grocery_list.items():
                    self.list_box.insert(tk.END, f'{item} - {values["category"]} - {values["quantity"]}')

    def edit_item(self):
        try:
            selected_index = self.list_box.curselection()[0]
            item = self.list_box.get(selected_index).split(' - ')[0]
            category = self.grocery_list[item]['category']
            quantity = self.grocery_list[item]['quantity']

            edit_window = tk.Toplevel(self.root)
            edit_window.title('Edit Item')

            item_label = ttk.Label(edit_window, text='Item:')
            item_label.pack(padx=10, pady=10)

            item_entry = ttk.Entry(edit_window, width=20)
            item_entry.insert(tk.END, item)
            item_entry.pack(padx=10, pady=10)

            category_label = ttk.Label(edit_window, text='Category:')
            category_label.pack(padx=10, pady=10)

            category_entry = ttk.Entry(edit_window, width=20)
            category_entry.insert(tk.END, category)
            category_entry.pack(padx=10, pady=10)

            quantity_label = ttk.Label(edit_window, text='Quantity:')
            quantity_label.pack(padx=10, pady=10)

            quantity_entry = ttk.Entry(edit_window, width=5)
            quantity_entry.insert(tk.END, quantity)
            quantity_entry.pack(padx=10, pady=10)

            def save_changes():
                new_item = item_entry.get()
                new_category = category_entry.get()
                new_quantity = quantity_entry.get()

                if new_item and new_category and new_quantity:
                    del self.grocery_list[item]
                    self.grocery_list[new_item] = {'category': new_category, 'quantity': new_quantity}
                    self.list_box.delete(selected_index)
                    self.list_box.insert(selected_index, f'{new_item} - {new_category} - {new_quantity}')
                    edit_window.destroy()
                else:
                    messagebox.showerror('Error', 'Please fill out all fields')

            save_button = ttk.Button(edit_window, text='Save Changes', command=save_changes)
            save_button.pack(padx=10, pady=10)

        except IndexError:
            messagebox.showerror('Error', 'Please select an item to edit')

if __name__ == '__main__':
    root = tk.Tk()
    app = GroceryListApp(root)
    root.mainloop()
