import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import colorsys

class TimelineTab(ttk.Frame):
    def __init__(self, parent, conn, company_colors, update_callback):
        super().__init__(parent)
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.company_colors = company_colors
        self.update_callback = update_callback
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        input_frame = ttk.Frame(self, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")

        # First row
        ttk.Label(input_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        # Second row
        ttk.Label(input_frame, text="Event Description:").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.event_description = tk.Entry(input_frame, width=40)
        self.event_description.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Third row
        ttk.Label(input_frame, text="Company:").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.event_company_var = tk.StringVar()
        self.event_company_combobox = ttk.Combobox(input_frame, textvariable=self.event_company_var, width=38)
        self.event_company_combobox.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Fourth row
        ttk.Button(input_frame, text="Add Event", command=self.add_timeline_event).grid(row=3, column=0, columnspan=4, pady=10)

        # Timeline display
        self.timeline_canvas = tk.Canvas(self, bg="white")
        self.timeline_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Bind the canvas resizing to the window resize event
        self.timeline_canvas.bind("<Configure>", self.load_timeline)

        self.load_companies()
        self.load_timeline()

    def load_companies(self):
        try:
            self.cursor.execute("SELECT name FROM companies")
            companies = [row[0] for row in self.cursor.fetchall()]
            self.event_company_combobox['values'] = companies
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading companies: {e}")

    def update_companies(self, companies):
        self.event_company_combobox['values'] = companies

    def add_timeline_event(self):
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            description = self.event_description.get()
            company = self.event_company_var.get()

            if not description:
                raise ValueError("Description cannot be empty")

            if start_date > end_date:
                raise ValueError("Start date must be before end date")

            self.cursor.execute("INSERT INTO timeline (start_date, end_date, description, company) VALUES (?, ?, ?, ?)",
                                (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), description, company))
            self.conn.commit()
            self.load_timeline()
            self.event_description.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while adding the event: {e}")

    def load_timeline(self, event=None):
        try:
            self.timeline_canvas.delete("all")
            self.cursor.execute("SELECT * FROM timeline ORDER BY start_date")
            events = self.cursor.fetchall()

            if not events:
                self.timeline_canvas.create_text(400, 200, text="No events to display", font=("Arial", 14))
                return

            min_date = min(datetime.strptime(event[1], "%Y-%m-%d") for event in events)
            max_date = max(datetime.strptime(event[2], "%Y-%m-%d") for event in events)
            total_days = (max_date - min_date).days + 1

            canvas_width = self.timeline_canvas.winfo_width()
            canvas_height = self.timeline_canvas.winfo_height()
            left_margin = 100
            right_margin = 50
            top_margin = 50
            bottom_margin = 80
            day_width = (canvas_width - left_margin - right_margin) / total_days

            # Draw events
            for i, event in enumerate(events):
                start = datetime.strptime(event[1], "%Y-%m-%d")
                end = datetime.strptime(event[2], "%Y-%m-%d")
                description = event[3]
                company = event[4]

                start_x = left_margin + (start - min_date).days * day_width
                end_x = left_margin + ((end - min_date).days + 1) * day_width
                y = top_margin + i * 30

                color = self.get_company_color(company)
                self.timeline_canvas.create_rectangle(start_x, y, end_x, y+20, fill=color, outline="black")
                self.timeline_canvas.create_text((start_x + end_x)/2, y+10, text=description, font=("Arial", 8))

            # Draw time axis
            axis_y = canvas_height - bottom_margin
            self.timeline_canvas.create_line(left_margin, axis_y, canvas_width - right_margin, axis_y, arrow=tk.LAST)

            # Draw start and end dates
            self.timeline_canvas.create_text(left_margin, axis_y + 20, text=min_date.strftime("%Y-%m-%d"), anchor="nw", font=("Arial", 8))
            self.timeline_canvas.create_text(canvas_width - right_margin, axis_y + 20, text=max_date.strftime("%Y-%m-%d"), anchor="ne", font=("Arial", 8))

            # Draw intermediate dates
            for i in range(total_days):
                x = left_margin + i * day_width
                date = min_date + timedelta(days=i)
                if i % 30 == 0 and i != 0:  # Label every 30 days, but not the start date
                    self.timeline_canvas.create_line(x, axis_y, x, axis_y-10)
                    self.timeline_canvas.create_text(x, axis_y + 20, text=date.strftime("%Y-%m-%d"), angle=45, anchor="ne", font=("Arial", 8))

            # Draw company labels (key)
            for i, company in enumerate(set(event[4] for event in events)):
                y = top_margin + i * 30
                color = self.get_company_color(company)
                self.timeline_canvas.create_rectangle(10, y, 90, y+20, fill=color, outline="black")
                self.timeline_canvas.create_text(50, y+10, text=company, font=("Arial", 8))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while loading the timeline: {e}")

    def get_company_color(self, company):
        try:
            self.cursor.execute("SELECT color FROM companies WHERE name=?", (company,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
        except sqlite3.Error:
            pass

        # If no color is found or there's an error, generate a color
        if company not in self.company_colors:
            hue = hash(company) % 100 / 100.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
            self.company_colors[company] = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        return self.company_colors[company]
