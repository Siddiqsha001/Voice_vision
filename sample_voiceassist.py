import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
import csv
import sqlite3

# Define colors for the UI
bg_color = '#f0f0f0'
frame_bg_color = '#e0e0e0'
button_color = '#4CAF50'
button_hover_color = '#45a049'
text_color = '#333333'
highlight_color = '#FFD700'

# Initialize the main application window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("900x700")
root.config(bg=bg_color)

# Initialize the SQLite database
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    total_salary REAL DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category_id INTEGER,
    amount REAL,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS salary_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    salary REAL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Initialize data structures
current_user = None

# Function to show a frame
def show_frame(frame):
    frame.tkraise()

# Function to create a styled button with hover effects
def create_button(parent, text, command, bg_color, hover_color, **kwargs):
    def on_enter(e):
        btn.config(bg=hover_color)
    def on_leave(e):
        btn.config(bg=bg_color)
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg='white', **kwargs)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# Define the LoginPage class
class LoginPage(tk.Frame):
    def init(self, parent, controller):
        tk.Frame.init(self, parent)
        self.controller = controller
        self.config(bg=bg_color)
        
        tk.Label(self, text="Login", bg=bg_color, font=("Helvetica", 18, 'bold')).pack(pady=10)
        
        tk.Label(self, text="Username", bg=bg_color).pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        
        tk.Label(self, text="Password", bg=bg_color).pack(pady=5)
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack(pady=5)
        
        self.login_button = create_button(self, "Login", self.login_user, button_color, button_hover_color, width=20)
        self.login_button.pack(pady=5)
        
        self.register_button = create_button(self, "Register", lambda: show_frame(frames["RegisterPage"]), '#2196f3', '#1e88e5', width=20)
        self.register_button.pack(pady=5)
    
    def login_user(self):
        global current_user
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            current_user = user[0]  # user_id
            messagebox.showinfo("Success", f"Logged in as {username}")
            show_frame(frames["MainPage"])
            frames["MainPage"].update_recent_expenses()
        else:
            messagebox.showwarning("Login Error", "Incorrect username or password.")

# Define the RegisterPage class
class RegisterPage(tk.Frame):
    def init(self, parent, controller):
        tk.Frame.init(self, parent)
        self.controller = controller
        self.config(bg=bg_color)
        
        tk.Label(self, text="Register", bg=bg_color, font=("Helvetica", 18, 'bold')).pack(pady=10)
        
        tk.Label(self, text="Username", bg=bg_color).pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        
        tk.Label(self, text="Password", bg=bg_color).pack(pady=5)
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack(pady=5)
        
        self.register_button = create_button(self, "Register", self.register_user, button_color, button_hover_color, width=20)
        self.register_button.pack(pady=5)
        
        self.login_button = create_button(self, "Back to Login", lambda: show_frame(frames["LoginPage"]), '#2196f3', '#1e88e5', width=20)
        self.login_button.pack(pady=5)
    
    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            messagebox.showwarning("Registration Error", "Username already exists.")
            return
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully.")
        show_frame(frames["LoginPage"])

# Define the MainPage class
class MainPage(tk.Frame):
    def init(self, parent, controller):
        tk.Frame.init(self, parent)
        self.controller = controller
        self.config(bg=bg_color)
        
        self.frame = tk.Frame(self, bg=bg_color)
        self.frame.pack(pady=20)
        
        create_button(self.frame, "Set Salary", self.set_salary, '#9c27b0', '#8e24aa', width=20).grid(row=0, column=0, padx=10, pady=5)
        create_button(self.frame, "Manage Categories", self.manage_categories, '#009688', '#00897b', width=20).grid(row=0, column=1, padx=10, pady=5)
        create_button(self.frame, "Add Expense", self.add_expense, '#ff9800', '#fb8c00', width=20).grid(row=1, column=0, padx=10, pady=5)
        create_button(self.frame, "Show Summary", self.show_summary, '#795548', '#6d4c41', width=20).grid(row=1, column=1, padx=10, pady=5)
        create_button(self.frame, "Monthly Expenses", self.show_monthly_expenses, '#607d8b', '#546e7a', width=20).grid(row=2, column=0, padx=10, pady=5)
        create_button(self.frame, "Predict Salary", self.predict_salary, '#3f51b5', '#3949ab', width=20).grid(row=2, column=1, padx=10, pady=5)
        create_button(self.frame, "Export to CSV", self.export_to_csv, '#f44336', '#e53935', width=20).grid(row=3, column=0, padx=10, pady=5)
        
        tk.Label(self, text="Recent Expenses", bg=bg_color, font=("Helvetica", 18, 'bold')).pack(pady=10)
        self.recent_expenses_listbox = tk.Listbox(self, width=50, height=10, font=("Helvetica", 12))
        self.recent_expenses_listbox.pack()
    
    def set_salary(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        while True:
            try:
                salary = float(simpledialog.askstring("Salary Input", "Please enter your total salary ($):", parent=self))
                cursor.execute('UPDATE users SET total_salary = ? WHERE id = ?', (salary, current_user))
                conn.commit()
                cursor.execute('INSERT INTO salary_history (user_id, salary) VALUES (?, ?)', (current_user, salary))
                conn.commit()
                break
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid salary amount.")
        messagebox.showinfo("Success", f"Total salary set to: ${salary:.2f}")
    
    def manage_categories(self):
        def add_category():
            new_category = category_entry.get()
            if new_category:
                cursor.execute('INSERT INTO categories (name) VALUES (?)', (new_category,))
                conn.commit()
                category_entry.delete(0, tk.END)
                update_categories_listbox()
            else:
                messagebox.showwarning("Input Error", "Please enter a category name.")
        
        def delete_category():
            selected_category = categories_listbox.get(tk.ACTIVE)
            if selected_category:
                cursor.execute('DELETE FROM categories WHERE name = ?', (selected_category,))
                conn.commit()
                update_categories_listbox()
            else:
                messagebox.showwarning("Selection Error", "Please select a category to delete.")
        
        def update_categories_listbox():
            categories_listbox.delete(0, tk.END)
            cursor.execute('SELECT name FROM categories')
            for category in cursor.fetchall():
                categories_listbox.insert(tk.END, category[0])
        
        manage_categories_window = tk.Toplevel(self)
        manage_categories_window.title("Manage Categories")
        
        tk.Label(manage_categories_window, text="Add Category").pack(pady=5)
        category_entry = tk.Entry(manage_categories_window)
        category_entry.pack(pady=5)
        create_button(manage_categories_window, "Add", add_category, button_color, button_hover_color).pack(pady=5)
        
        tk.Label(manage_categories_window, text="Existing Categories").pack(pady=5)
        categories_listbox = tk.Listbox(manage_categories_window)
        categories_listbox.pack(pady=5)
        create_button(manage_categories_window, "Delete", delete_category, '#f44336', '#e53935').pack(pady=5)
        
        update_categories_listbox()
    
    def add_expense(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        def save_expense():
            category = category_combobox.get()
            amount = amount_entry.get()
            date = date_entry.get()
            if not category or not amount or not date:
                messagebox.showwarning("Input Error", "Please fill out all fields.")
                return
            try:
                amount = float(amount)
                cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
                category_id = cursor.fetchone()[0]
                cursor.execute('INSERT INTO expenses (user_id, category_id, amount, date) VALUES (?, ?, ?, ?)',
                               (current_user, category_id, amount, date))
                conn.commit()
                messagebox.showinfo("Success", "Expense added successfully.")
                add_expense_window.destroy()
                self.update_recent_expenses()
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid amount.")
        
        add_expense_window = tk.Toplevel(self)
        add_expense_window.title("Add Expense")
        
        tk.Label(add_expense_window, text="Category").pack(pady=5)
        cursor.execute('SELECT name FROM categories')
        categories = [row[0] for row in cursor.fetchall()]
        category_combobox = ttk.Combobox(add_expense_window, values=categories)
        category_combobox.pack(pady=5)
        
        tk.Label(add_expense_window, text="Amount").pack(pady=5)
        amount_entry = tk.Entry(add_expense_window)
        amount_entry.pack(pady=5)
        
        tk.Label(add_expense_window, text="Date").pack(pady=5)
        date_entry = DateEntry(add_expense_window)
        date_entry.pack(pady=5)
        
        create_button(add_expense_window, "Save", save_expense, button_color, button_hover_color).pack(pady=5)
    
    def show_summary(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        cursor.execute('''
        SELECT c.name, SUM(e.amount) 
        FROM expenses e 
        JOIN categories c ON e.category_id = c.id 
        WHERE e.user_id = ? 
        GROUP BY c.name
        ''', (current_user,))
        summary = cursor.fetchall()
        
        categories = [row[0] for row in summary]
        amounts = [row[1] for row in summary]
        
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        
        summary_window = tk.Toplevel(self)
        summary_window.title("Expense Summary")
        
        canvas = FigureCanvasTkAgg(fig, master=summary_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def show_monthly_expenses(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        cursor.execute('''
        SELECT strftime('%Y-%m', e.date) as month, SUM(e.amount)
        FROM expenses e
        WHERE e.user_id = ?
        GROUP BY month
        ORDER BY month
        ''', (current_user,))
        monthly_expenses = cursor.fetchall()
        
        months = [row[0] for row in monthly_expenses]
        amounts = [row[1] for row in monthly_expenses]
        
        fig, ax = plt.subplots()
        ax.plot(months, amounts, marker='o')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount Spent ($)')
        ax.set_title('Monthly Expenses')
        
        monthly_expenses_window = tk.Toplevel(self)
        monthly_expenses_window.title("Monthly Expenses")
        
        canvas = FigureCanvasTkAgg(fig, master=monthly_expenses_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def predict_salary(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        cursor.execute('SELECT salary FROM salary_history WHERE user_id = ?', (current_user,))
        salary_history = cursor.fetchall()
        
        if len(salary_history) < 2:
            messagebox.showwarning("Insufficient Data", "At least 2 salary entries are required for prediction.")
            return
        
        X = np.array(range(len(salary_history))).reshape(-1, 1)
        y = np.array([entry[0] for entry in salary_history])
        
        model = LinearRegression()
        model.fit(X, y)
        
        next_month = len(salary_history)
        predicted_salary = model.predict([[next_month]])[0]
        
        messagebox.showinfo("Predicted Salary", f"Predicted Salary for next month: ${predicted_salary:.2f}")
    
    def export_to_csv(self):
        global current_user
        if not current_user:
            messagebox.showwarning("Login Required", "Please login first.")
            return
        cursor.execute('''
        SELECT e.id, u.username, c.name, e.amount, e.date
        FROM expenses e
        JOIN users u ON e.user_id = u.id
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
        ''', (current_user,))
        expenses = cursor.fetchall()
        
        if not expenses:
            messagebox.showinfo("No Data", "No expenses to export.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", ".csv"), ("All files", ".*")])
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Username', 'Category', 'Amount', 'Date'])
                writer.writerows(expenses)
            messagebox.showinfo("Export Successful", "Expenses exported to CSV successfully.")
    
    def update_recent_expenses(self):
        self.recent_expenses_listbox.delete(0, tk.END)
        cursor.execute('''
        SELECT c.name, e.amount, e.date
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = ?
        ORDER BY e.date DESC
        LIMIT 10
        ''', (current_user,))
        recent_expenses = cursor.fetchall()
        for expense in recent_expenses:
            self.recent_expenses_listbox.insert(tk.END, f"{expense[0]}: ${expense[1]:.2f} on {expense[2]}")

# Initialize frames
frames = {}
for F in (LoginPage, RegisterPage, MainPage):
    page_name = F.name
    frame = F(parent=root, controller=root)
    frames[page_name] = frame
    frame.grid(row=0, column=0, sticky="nsew")

# Start with LoginPage
show_frame(frames["LoginPage"])

root.mainloop()