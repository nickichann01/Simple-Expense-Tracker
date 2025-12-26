import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("DiBiLi - Divide it. Budget it. Live easy")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.low_balance_threshold = 100.0  # Threshold for low balance warning
        
        # Modern UI Theme Setup
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
        style.configure('TFrame', background='#f0f0f0')  # Light gray background
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6, relief='flat', background='#4CAF50', foreground='white')
        style.map('TButton', background=[('active', '#45a049')])  # Hover effect
        style.configure('TEntry', font=('Segoe UI', 10), padding=5)
        style.configure('TRadiobutton', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TNotebook', background='#f0f0f0', tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[10, 5])
        
        # Load existing transactions from file
        self.transactions = self.load_data()
        
        self.main_frame = ttk.Frame(root, padding="20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with modern styling
        self.header_label = ttk.Label(self.main_frame, text="💰 DiBiLi - Daily Expense Tracker", font=("Segoe UI", 18, "bold"), foreground='#333')
        self.header_label.pack(pady=(0, 20))
        
        # Summary Frame with card-like design
        self.summary_frame = ttk.Frame(self.main_frame, padding="15", relief="raised", borderwidth=2, style='TFrame')
        self.summary_frame.pack(pady=10, fill=tk.X)
        self.summary_frame.configure(style='Card.TFrame')  # Custom style for card effect
        
        self.label_income = ttk.Label(self.summary_frame, text="Total Income: Php 0.00", font=("Segoe UI", 12, "bold"), foreground='#4CAF50')
        self.label_income.pack(side=tk.LEFT, padx=35)
        
        self.label_expenses = ttk.Label(self.summary_frame, text="Total Expenses: Php 0.00", font=("Segoe UI", 12, "bold"), foreground='#f44336')
        self.label_expenses.pack(side=tk.LEFT, padx=35)
        
        self.label_balance = ttk.Label(self.summary_frame, text="Balance: Php 0.00", font=("Segoe UI", 12, "bold"), foreground='#2196F3')
        self.label_balance.pack(side=tk.LEFT, padx=35)
        
        # Form Frame with modern layout
        self.form_frame = ttk.Frame(self.main_frame, padding="15", relief="raised", borderwidth=2, style='TFrame')
        self.form_frame.pack(pady=10, fill=tk.X)
        
        # Configure grid weights for stretching
        self.form_frame.columnconfigure(1, weight=1)
        
        # Transaction Type
        ttk.Label(self.form_frame, text="Transaction Type:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        radio_frame = ttk.Frame(self.form_frame, style='TFrame')
        radio_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(radio_frame, text="💼 Income", variable=self.type_var, value="income").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="🛒 Expense", variable=self.type_var, value="expense").pack(side=tk.LEFT)
        
        # Date
        ttk.Label(self.form_frame, text="Date (YYYY-MM-DD):", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(self.form_frame, width=50)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)
        
        # Amount
        ttk.Label(self.form_frame, text="Amount (Php):", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_entry = tk.Entry(self.form_frame, width=50, font=('Segoe UI', 11), bg='white', fg='gray')
        self.amount_entry.insert(0, "Enter amount...")
        self.amount_entry.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=5)
        self.amount_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.amount_entry, "Enter amount..."))
        self.amount_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.amount_entry, "Enter amount..."))
        
        # Item
        ttk.Label(self.form_frame, text="Item/Description:", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.desc_entry = tk.Entry(self.form_frame, width=50, font=('Segoe UI', 11), bg='white', fg='gray')
        self.desc_entry.insert(0, "Enter item...")
        self.desc_entry.grid(row=3, column=1, columnspan=2, sticky=tk.EW, pady=5)
        self.desc_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.desc_entry, "Enter item..."))
        self.desc_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.desc_entry, "Enter item..."))
        
        # Buttons with modern styling, centered
        button_frame = ttk.Frame(self.form_frame, style='TFrame')
        button_frame.grid(row=4, column=0, columnspan=3, pady=15, sticky=tk.EW)
        self.add_button = ttk.Button(button_frame, text="➕ Add Transaction", command=self.add_transaction, width=18)
        self.add_button.pack(anchor=tk.CENTER)
        self.delete_all_button = ttk.Button(button_frame, text="🗑️ Delete All", command=self.delete_all_transactions, width=18, style='Danger.TButton')
        self.delete_all_button.pack(anchor=tk.CENTER, pady=(10, 0))  # Add some vertical space
        
        # List Frame
        self.list_frame = ttk.Frame(self.main_frame, padding="10", relief="raised", borderwidth=2, style='TFrame')
        self.list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.list_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.check_salary()
        self.update_display()
        
        # Custom styles for danger button
        style.configure('Danger.TButton', background='#f44336', foreground='white')
        style.map('Danger.TButton', background=[('active', '#d32f2f')])
        style.configure('Card.TFrame', background='#ffffff', relief='raised', borderwidth=1)

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground='black')  # Set text color to black when clearing placeholder
    
    def restore_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.configure(foreground='gray')  # Set placeholder text to gray
    
    def load_data(self):
        try:
            with open('transactions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_data(self):
        with open('transactions.json', 'w') as f:
            json.dump(self.transactions, f)
    
    def add_transaction(self):
        type_ = self.type_var.get()
        date_str = self.date_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if amount_str == "Enter amount...":
            amount_str = ""
        if description == "Enter item...":
            description = ""
        
        try:
            transaction_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
        
        # Check if the date is advance
        today = datetime.date.today()
        if transaction_date > today:
            messagebox.showerror("Error", "Opps too advance! Please select today's date or earlier.")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            
            transaction = {
                'type': type_,
                'amount': amount,
                'date': date_str,
                'description': description
            }
            self.transactions.append(transaction)
            self.save_data()
            self.update_display()
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.configure(foreground='black')  # Ensure color is black after clearing
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.configure(foreground='black')  # Ensure color is black after clearing
            messagebox.showinfo("Success", "Transaction added!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}. Please enter a positive number for amount.")
    
    def update_display(self):
        total_income = sum(t['amount'] for t in self.transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in self.transactions if t['type'] == 'expense')
        balance = total_income - total_expenses
        self.label_income.config(text=f"Total Income: Php {total_income:.2f}")
        self.label_expenses.config(text=f"Total Expenses: Php {total_expenses:.2f}")
        self.label_balance.config(text=f"Balance: Php {balance:.2f}")
        
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        unique_dates = sorted(set(t['date'] for t in self.transactions))
        for date in unique_dates:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=date)
            
            listbox = tk.Listbox(frame, height=10, width=70, font=('Segoe UI', 9), bg='#f9f9f9', selectbackground='#4CAF50')
            listbox.pack(fill=tk.BOTH, expand=True)
            listbox.bind("<Double-1>", lambda event, lb=listbox, d=date: self.on_double_click(event, lb, d))  # Bind double-click
            
            date_transactions = [t for t in self.transactions if t['date'] == date]
            for t in date_transactions:
                listbox.insert(tk.END, f"{t['type'].capitalize()}: Php {t['amount']:.2f} - {t['description']}")
        
        if balance < self.low_balance_threshold:
            messagebox.showwarning(
                "Low Balance Alert",
                f"Warning: Your balance is below Php {self.low_balance_threshold:.2f}.\nCurrent balance: Php {balance:.2f}\nPlease add income or reduce expenses."
            )
    
    def on_double_click(self, event, listbox, date):
        selection = listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No transaction selected.")
            return
        index_in_listbox = selection[0]
        date_transactions = [t for t in self.transactions if t['date'] == date]
        if index_in_listbox < len(date_transactions):
            transaction = date_transactions[index_in_listbox]
            self.edit_transaction(transaction)
    
    def edit_transaction(self, transaction):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transaction")
        edit_window.geometry("450x400")
        edit_window.configure(bg='#f0f0f0')
        
        ttk.Label(edit_window, text="Type:", font=("Segoe UI", 11, "bold")).pack(pady=5)
        type_var = tk.StringVar(value=transaction['type'])
        ttk.Radiobutton(edit_window, text="💼 Income", variable=type_var, value="income").pack(anchor=tk.W)
        ttk.Radiobutton(edit_window, text="🛒 Expense", variable=type_var, value="expense").pack(anchor=tk.W)
        
        ttk.Label(edit_window, text="Date (YYYY-MM-DD):", font=("Segoe UI", 11, "bold")).pack(pady=5)
        date_entry = ttk.Entry(edit_window, width=35)
        date_entry.insert(0, transaction['date'])
        date_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Amount (Php):", font=("Segoe UI", 11, "bold")).pack(pady=5)
        amount_entry = ttk.Entry(edit_window, width=35)
        amount_entry.insert(0, str(transaction['amount']))
        amount_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Item/Description:", font=("Segoe UI", 11, "bold")).pack(pady=5)
        desc_entry = ttk.Entry(edit_window, width=35)
        desc_entry.insert(0, transaction['description'])
        desc_entry.pack(pady=5)
        
        def save_edited_transaction():
            try:
                new_type = type_var.get()
                new_date_str = date_entry.get().strip()
                new_amount_str = amount_entry.get().strip()
                new_description = desc_entry.get().strip()
                
                datetime.date.fromisoformat(new_date_str)  # Validate date
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    raise ValueError("Amount must be positive.")
                
                # Check if the date is in the future
                new_date = datetime.date.fromisoformat(new_date_str)
                today = datetime.date.today()
                if new_date > today:
                    messagebox.showerror("Error", "You cannot enter a date in the future. Please select today's date or earlier.")
                    return
                
                # Update the transaction
                transaction['type'] = new_type
                transaction['date'] = new_date_str
                transaction['amount'] = new_amount
                transaction['description'] = new_description
                
                self.save_data()
                self.update_display()
                edit_window.destroy()
                messagebox.showinfo("Success", "Transaction updated!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
        
        def delete_single_transaction():
            response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
            if response:
                self.transactions.remove(transaction)
                self.save_data()
                self.update_display()
                edit_window.destroy()
                messagebox.showinfo("Success", "Transaction deleted!")
        
        button_frame = ttk.Frame(edit_window, style='TFrame')
        button_frame.pack(pady=15)
        ttk.Button(button_frame, text="💾 Save", command=save_edited_transaction, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=delete_single_transaction, width=12, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=edit_window.destroy, width=12).pack(side=tk.LEFT, padx=5)
    
    def delete_all_transactions(self):
        if not self.transactions:
            messagebox.showinfo("No Transactions", "There are no transactions to delete.")
            return
        response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all transactions? This action cannot be undone.")
        if response:
            self.transactions = []
            self.save_data()
            self.update_display()
            messagebox.showinfo("Success", "All transactions deleted!")
    
    def check_salary(self):
        today = datetime.date.today().isoformat()
        if today in [t['date'] for t in self.transactions if t['type'] == 'income']:
            return
        if datetime.date.today().day in [15, 30]:
            response = messagebox.askyesno("Salary Reminder", f"Today is the {datetime.date.today().day}th. Do you want to add your salary income?")
            if response:
                amount = simpledialog.askfloat("Enter Salary", "Enter your salary amount:", parent=self.root)
                if amount and amount > 0:
                    transaction = {'type': 'income', 'amount': amount, 'date': today, 'description': 'Salary'}
                    self.transactions.append(transaction)
                    self.save_data()
                    self.update_display()
                    messagebox.showinfo("Success", "Salary added!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

    # Yow to someone who's here i've been developing this since August 2025.