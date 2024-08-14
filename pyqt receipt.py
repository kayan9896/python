
from datetime import date

class Receipt:
    def __init__(self, item_name, purchase_date, total_cost, image_path=None, description=None):
        self.item_name = item_name
        self.purchase_date = purchase_date
        self.total_cost = total_cost
        self.image_path = image_path
        self.description = description

    def __str__(self):
        return f"Item: {self.item_name}, Date: {self.purchase_date}, Cost: ${self.total_cost:.2f}, Description: {self.description}"

class Paycheck:
    def __init__(self, payment_date, total_amount):
        self.payment_date = payment_date
        self.total_amount = total_amount

    def __str__(self):
        return f"Date: {self.payment_date}, Amount: ${self.total_amount:.2f}"

import sys
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QCheckBox, QHBoxLayout, QPushButton, QDateEdit, QMessageBox, QFileDialog, QLabel
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator

class ReceiptManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Receipt Manager")
        self.setGeometry(100, 100, 600, 400)

        self.receipts = []
        self.paychecks = []

        layout = QVBoxLayout()

        # Create a checkbox to toggle the visibility of entry boxes for adding new receipts
        self.add_receipt_checkbox = QCheckBox("Add New Receipt")
        self.add_receipt_checkbox.stateChanged.connect(self.toggle_entry_boxes)
        layout.addWidget(self.add_receipt_checkbox)

        # Create entry boxes for adding new receipts
        self.entry_layout = QHBoxLayout()
        self.item_entry = QLineEdit()
        self.item_entry.setPlaceholderText("Item")
        self.entry_layout.addWidget(self.item_entry)
        self.date_entry = QDateEdit()
        self.date_entry.setCalendarPopup(True)
        self.date_entry.setDate(QDate.currentDate())
        self.entry_layout.addWidget(self.date_entry)
        self.cost_entry = QLineEdit()
        self.cost_entry.setPlaceholderText("Total Cost")
        self.cost_entry.setValidator(QDoubleValidator())
        self.entry_layout.addWidget(self.cost_entry)
        self.image_entry = QLineEdit()
        self.image_entry.setPlaceholderText("Image Path")
        self.entry_layout.addWidget(self.image_entry)
        self.description_entry = QLineEdit()
        self.description_entry.setPlaceholderText("Description")
        self.entry_layout.addWidget(self.description_entry)
        layout.addLayout(self.entry_layout)

        # Create an "Add Receipt" button
        self.add_button = QPushButton("Add Receipt")
        self.add_button.clicked.connect(self.add_receipt)
        layout.addWidget(self.add_button)

        # Create a checkbox to toggle the visibility of entry boxes for adding new paychecks
        self.add_paycheck_checkbox = QCheckBox("Add New Paycheck")
        self.add_paycheck_checkbox.stateChanged.connect(self.toggle_paycheck_entry_boxes)
        layout.addWidget(self.add_paycheck_checkbox)

        # Create entry boxes for adding new paychecks
        self.paycheck_entry_layout = QHBoxLayout()
        self.payment_date_entry = QDateEdit()
        self.payment_date_entry.setCalendarPopup(True)
        self.payment_date_entry.setDate(QDate.currentDate())
        self.paycheck_entry_layout.addWidget(self.payment_date_entry)
        self.paycheck_amount_entry = QLineEdit()
        self.paycheck_amount_entry.setPlaceholderText("Total Amount")
        self.paycheck_amount_entry.setValidator(QDoubleValidator())
        self.paycheck_entry_layout.addWidget(self.paycheck_amount_entry)
        layout.addLayout(self.paycheck_entry_layout)

        # Create an "Add Paycheck" button
        self.add_paycheck_button = QPushButton("Add Paycheck")
        self.add_paycheck_button.clicked.connect(self.add_paycheck)
        layout.addWidget(self.add_paycheck_button)

        # Create a table widget to display the receipts and paychecks
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Create a "Print Receipts" button
        self.print_receipts_button = QPushButton("Print Receipts")
        self.print_receipts_button.clicked.connect(self.print_receipts)
        layout.addWidget(self.print_receipts_button)

        # Create a "Delete Receipt" button
        self.delete_button = QPushButton("Delete Receipt")
        self.delete_button.clicked.connect(self.delete_receipt)
        layout.addWidget(self.delete_button)

        # Create a "Save to CSV" button
        self.save_csv_button = QPushButton("Save to CSV")
        self.save_csv_button.clicked.connect(self.save_to_csv)
        layout.addWidget(self.save_csv_button)

        # Create a "Load from CSV" button
        self.load_csv_button = QPushButton("Load from CSV")
        self.load_csv_button.clicked.connect(self.load_from_csv)
        layout.addWidget(self.load_csv_button)

        # Create a "Switch to Paychecks" button
        self.switch_to_paychecks_button = QPushButton("Switch to Paychecks")
        self.switch_to_paychecks_button.clicked.connect(self.switch_to_paychecks)
        layout.addWidget(self.switch_to_paychecks_button)

        # Create a "Switch to Receipts" button
        self.switch_to_receipts_button = QPushButton("Switch to Receipts")
        self.switch_to_receipts_button.clicked.connect(self.switch_to_receipts)
        layout.addWidget(self.switch_to_receipts_button)

        # Create a label to display the total sum of paychecks
        self.total_paycheck_label = QLabel()
        layout.addWidget(self.total_paycheck_label)

        # Create a label to display the total sum of receipts
        self.total_receipt_label = QLabel()
        layout.addWidget(self.total_receipt_label)

        self.setLayout(layout)

        self.toggle_entry_boxes()  # Hide receipt entry boxes initially
        self.toggle_paycheck_entry_boxes()  # Hide paycheck entry boxes initially
        self.switch_to_receipts()  # Show receipts table initially

    def toggle_entry_boxes(self):
        if self.add_receipt_checkbox.isChecked():
            self.item_entry.setVisible(True)
            self.date_entry.setVisible(True)
            self.cost_entry.setVisible(True)
            self.image_entry.setVisible(True)
            self.description_entry.setVisible(True)
            self.add_button.setVisible(True)
        else:
            self.item_entry.setVisible(False)
            self.date_entry.setVisible(False)
            self.cost_entry.setVisible(False)
            self.image_entry.setVisible(False)
            self.description_entry.setVisible(False)
            self.add_button.setVisible(False)

    def add_receipt(self):
        item = self.item_entry.text().strip()
        date = self.date_entry.date().toString("yyyy-MM-dd")
        cost_text = self.cost_entry.text().strip()

        if not item or not date or not cost_text:
            missing_info = "Please provide the following information:\n"
            if not item:
                missing_info += "- Item name\n"
            if not date:
                missing_info += "- Purchase date\n"
            if not cost_text:
                missing_info += "- Total cost\n"
            QMessageBox.warning(self, "Missing Information", missing_info)
            return

        try:
            cost = float(cost_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Cost", "Please enter a valid number for the total cost.")
            return

        image_path = self.image_entry.text()
        description = self.description_entry.text()

        new_receipt = Receipt(item, date, cost, image_path, description)
        self.receipts.append(new_receipt)
        self.populate_table()
        self.update_total_receipt_label()  # Update the total receipt label after adding a new receipt

        self.clear_entry_boxes()

    def clear_entry_boxes(self):
        self.item_entry.clear()
        self.date_entry.setDate(QDate.currentDate())
        self.cost_entry.clear()
        self.image_entry.clear()
        self.description_entry.clear()

    def populate_table(self):
        self.table.setRowCount(len(self.receipts))
        for row, receipt in enumerate(self.receipts):
            self.table.setItem(row, 0, QTableWidgetItem(receipt.item_name))
            self.table.setItem(row, 1, QTableWidgetItem(receipt.purchase_date))
            self.table.setItem(row, 2, QTableWidgetItem(str(receipt.total_cost)))
            self.table.setItem(row, 3, QTableWidgetItem(receipt.image_path))
            self.table.setItem(row, 4, QTableWidgetItem(receipt.description))
        self.table.resizeColumnsToContents()

    def update_receipt(self, item):
        row = item.row()
        col = item.column()
        receipt = self.receipts[row]

        if col == 0:
            receipt.item_name = item.text()
        elif col == 1:
            receipt.purchase_date = item.text()
        elif col == 2:
            try:
                receipt.total_cost = float(item.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid Cost", "Please enter a valid number for the total cost.")
                self.populate_table()  # Refresh the table to revert the changes
        elif col == 3:
            receipt.image_path = item.text()
        elif col == 4:
            receipt.description = item.text()

    def delete_receipt(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        confirmed = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete the selected receipt(s)?")
        if confirmed == QMessageBox.Yes:
            for row in sorted(set([row.row() for row in selected_rows]), reverse=True):
                self.receipts.pop(row)
            self.populate_table()
            self.update_total_receipt_label()  # Update the total receipt label after deleting a receipt

    def save_to_csv(self):
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix("csv")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV Files (*.csv)")

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            try:
                if self.table.columnCount() == 5:  # Receipts table is displayed
                    self.save_receipts_to_csv(selected_file)
                elif self.table.columnCount() == 2:  # Paychecks table is displayed
                    self.save_paychecks_to_csv(selected_file)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save data to CSV: {str(e)}")

    def save_receipts_to_csv(self, file_path):
        with open(file_path, "w", newline="") as csv_file:
            fieldnames = ["Item", "Purchase Date", "Total Cost", "Image Path", "Description"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for receipt in self.receipts:
                writer.writerow({
                    "Item": receipt.item_name,
                    "Purchase Date": receipt.purchase_date,
                    "Total Cost": str(receipt.total_cost),
                    "Image Path": receipt.image_path,
                    "Description": receipt.description
                })

        QMessageBox.information(self, "Success", f"Receipts saved to {file_path}")

    def save_paychecks_to_csv(self, file_path):
        with open(file_path, "w", newline="") as csv_file:
            fieldnames = ["Payment Date", "Total Amount"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for paycheck in self.paychecks:
                writer.writerow({
                    "Payment Date": paycheck.payment_date,
                    "Total Amount": str(paycheck.total_amount)
                })

        QMessageBox.information(self, "Success", f"Paychecks saved to {file_path}")

    def load_from_csv(self):
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix("csv")
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setNameFilter("CSV Files (*.csv)")

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            try:
                with open(selected_file, "r") as csv_file:
                    reader = csv.DictReader(csv_file)
                    if self.table.columnCount() == 5:  # Receipts table is displayed
                        self.load_receipts_from_csv(reader)
                    elif self.table.columnCount() == 2:  # Paychecks table is displayed
                        self.load_paychecks_from_csv(reader)
                QMessageBox.information(self, "Success", f"Data loaded from {selected_file}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load data from CSV: {str(e)}")

    def load_receipts_from_csv(self, reader):
        self.receipts = []
        for row in reader:
            item_name = row["Item"]
            purchase_date = row["Purchase Date"]
            total_cost = float(row["Total Cost"])
            image_path = row["Image Path"]
            description = row["Description"]
            receipt = Receipt(item_name, purchase_date, total_cost, image_path, description)
            self.receipts.append(receipt)
        self.populate_table()
        self.update_total_receipt_label()  # Update the total receipt label after loading receipts

    def load_paychecks_from_csv(self, reader):
        self.paychecks = []
        for row in reader:
            payment_date = row["Payment Date"]
            total_amount = float(row["Total Amount"])
            paycheck = Paycheck(payment_date, total_amount)
            self.paychecks.append(paycheck)
        self.populate_paychecks_table()

    def switch_to_paychecks(self):
        self.add_receipt_checkbox.setChecked(False)  # Uncheck the "Add New Receipt" checkbox
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Payment Date", "Total Amount"])
        self.populate_paychecks_table()
        self.switch_to_receipts_button.setVisible(True)
        self.switch_to_paychecks_button.setVisible(False)
        self.add_receipt_checkbox.setVisible(False)
        self.add_paycheck_checkbox.setVisible(True)
        self.total_paycheck_label.setVisible(True)  # Show the total paycheck label
        self.total_receipt_label.setVisible(False)  # Hide the total receipt label
        self.toggle_entry_boxes()
        self.toggle_paycheck_entry_boxes()
        self.update_total_paycheck_label()  # Update the total paycheck label

    def switch_to_receipts(self):
        self.add_paycheck_checkbox.setChecked(False)  # Uncheck the "Add New Paycheck" checkbox
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Item", "Purchase Date", "Total Cost", "Image Path", "Description"])
        self.populate_table()
        self.switch_to_receipts_button.setVisible(False)
        self.switch_to_paychecks_button.setVisible(True)
        self.add_receipt_checkbox.setVisible(True)
        self.add_paycheck_checkbox.setVisible(False)
        self.total_paycheck_label.setVisible(False)  # Hide the total paycheck label
        self.total_receipt_label.setVisible(True)  # Show the total receipt label
        self.toggle_entry_boxes()
        self.toggle_paycheck_entry_boxes()
        self.update_total_receipt_label()  # Update the total receipt label

    def toggle_paycheck_entry_boxes(self):
        if self.add_paycheck_checkbox.isChecked():
            self.payment_date_entry.setVisible(True)
            self.paycheck_amount_entry.setVisible(True)
            self.add_paycheck_button.setVisible(True)
        else:
            self.payment_date_entry.setVisible(False)
            self.paycheck_amount_entry.setVisible(False)
            self.add_paycheck_button.setVisible(False)

    def add_paycheck(self):
        payment_date = self.payment_date_entry.date().toString("yyyy-MM-dd")
        amount_text = self.paycheck_amount_entry.text().strip()

        if not payment_date or not amount_text:
            missing_info = "Please provide the following information:\n"
            if not payment_date:
                missing_info += "- Payment date\n"
            if not amount_text:
                missing_info += "- Total amount\n"
            QMessageBox.warning(self, "Missing Information", missing_info)
            return

        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid number for the total amount.")
            return

        new_paycheck = Paycheck(payment_date, amount)
        self.paychecks.append(new_paycheck)
        self.populate_paychecks_table()

        self.clear_paycheck_entry_boxes()
        self.update_total_paycheck_label()  # Update the total paycheck label after adding a new paycheck

    def clear_paycheck_entry_boxes(self):
        self.payment_date_entry.setDate(QDate.currentDate())
        self.paycheck_amount_entry.clear()

    def populate_paychecks_table(self):
        self.table.setRowCount(len(self.paychecks))
        for row, paycheck in enumerate(self.paychecks):
            self.table.setItem(row, 0, QTableWidgetItem(paycheck.payment_date))
            self.table.setItem(row, 1, QTableWidgetItem(str(paycheck.total_amount)))
        self.table.resizeColumnsToContents()

    def update_total_paycheck_label(self):
        total_amount = sum(paycheck.total_amount for paycheck in self.paychecks)
        self.total_paycheck_label.setText(f"Total Paychecks: ${total_amount:.2f}")

    def update_total_receipt_label(self):
        total_cost = sum(receipt.total_cost for receipt in self.receipts)
        self.total_receipt_label.setText(f"Total Receipts: ${total_cost:.2f}")

    def print_receipts(self):
        for receipt in self.receipts:
            print(receipt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    receipt_manager = ReceiptManager()
    receipt_manager.show()
    sys.exit(app.exec_())
