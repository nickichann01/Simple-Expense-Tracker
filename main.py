import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("DiBiLi - Divide it. Budget it. Live easy")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.low_balance_threshold = 100.0  # Threshold for low balance warning
        
        # Load existing transactions from file
        self.transactions = self.load_data()
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.header_label = ttk.Label(self.main_frame, text="Daily Expense Tracker", font=("Helvetica", 15, "bold"))
        self.header_label.pack(pady=10)
        
        self.summary_frame = ttk.Frame(self.main_frame, padding="10", relief="sunken", borderwidth=2)
        self.summary_frame.pack(pady=10, fill=tk.X)
        
        self.label_income = ttk.Label(self.summary_frame, text="Total Income: 0")
        self.label_income.pack(side=tk.LEFT, padx=90)
        
        self.label_expenses = ttk.Label(self.summary_frame, text="Total Expenses: 0")
        self.label_expenses.pack(side=tk.LEFT, padx=40)
        
        self.label_balance = ttk.Label(self.summary_frame, text="Balance: 0")
        self.label_balance.pack(side=tk.LEFT, padx=40)
        
        self.form_frame = ttk.Frame(self.main_frame, padding="10", relief="sunken", borderwidth=2)
        self.form_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(self.form_frame, text="Transaction Type:").pack(pady=5)
        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(self.form_frame, text="Income", variable=self.type_var, value="income").pack(anchor=tk.W)
        ttk.Radiobutton(self.form_frame, text="Expense", variable=self.type_var, value="expense").pack(anchor=tk.W)
        
        ttk.Label(self.form_frame, text="Date (YYYY-MM-DD):").pack(pady=5)
        self.date_entry = ttk.Entry(self.form_frame, width=60)
        self.date_entry.insert(0, datetime.date.today().isoformat())  # Default to today
        self.date_entry.pack(pady=5)
        
        ttk.Label(self.form_frame, text="Amount:").pack(pady=5)
        self.amount_entry = tk.Entry(self.form_frame, width=60)  # Changed to tk.Entry for color support
        self.amount_entry.insert(0, "Enter amount...")
        self.amount_entry.configure(foreground='gray')  # Set placeholder text to gray
        self.amount_entry.pack(pady=5)
        self.amount_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.amount_entry, "Enter amount..."))
        self.amount_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.amount_entry, "Enter amount..."))
        
        ttk.Label(self.form_frame, text="Item:").pack(pady=5)
        self.desc_entry = tk.Entry(self.form_frame, width=60)  # Changed to tk.Entry for color support
        self.desc_entry.insert(0, "Enter Item...")
        self.desc_entry.configure(foreground='gray')  # Set placeholder text to gray
        self.desc_entry.pack(pady=5)
        self.desc_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.desc_entry, "Enter Item..."))
        self.desc_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.desc_entry, "Enter Item..."))
        
        self.add_button = ttk.Button(self.form_frame, text="Add Transaction", command=self.add_transaction, width=20)
        self.add_button.pack(pady=10)
        
        # New button for deleting all transactions
        self.delete_all_button = ttk.Button(self.form_frame, text="Delete All Transactions", command=self.delete_all_transactions, width=20)
        self.delete_all_button.pack(pady=10)
        
        self.list_frame = ttk.Frame(self.main_frame, padding="10", relief="sunken", borderwidth=2)
        self.list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.list_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.check_salary()
        self.update_display()
    
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
        if description == "Enter Item...":
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
        self.label_income.config(text=f"Total Income: {total_income:.2f}")
        self.label_expenses.config(text=f"Total Expenses: {total_expenses:.2f}")
        self.label_balance.config(text=f"Balance: {balance:.2f}")
        
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        unique_dates = sorted(set(t['date'] for t in self.transactions))
        for date in unique_dates:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=date)
            
            listbox = tk.Listbox(frame, height=10, width=70)
            listbox.pack(fill=tk.BOTH, expand=True)
            listbox.bind("<Double-1>", lambda event, lb=listbox, d=date: self.on_double_click(event, lb, d))  # Bind double-click
            
            date_transactions = [t for t in self.transactions if t['date'] == date]
            for t in date_transactions:
                listbox.insert(tk.END, f"{t['type'].capitalize()}: {t['amount']:.2f} - {t['description']}")
        
        if balance < self.low_balance_threshold:
            messagebox.showwarning(
                "Low Balance Alert",
                f"Warning: Your balance is below ${self.low_balance_threshold:.2f}.\nCurrent balance: {balance:.2f}\nPlease add income or reduce expenses."
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
        edit_window.geometry("400x380")
        
        ttk.Label(edit_window, text="Type:").pack(pady=5)
        type_var = tk.StringVar(value=transaction['type'])
        ttk.Radiobutton(edit_window, text="Income", variable=type_var, value="income").pack(anchor=tk.W)
        ttk.Radiobutton(edit_window, text="Expense", variable=type_var, value="expense").pack(anchor=tk.W)
        
        ttk.Label(edit_window, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(edit_window, width=30)
        date_entry.insert(0, transaction['date'])
        date_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Amount:").pack(pady=5)
        amount_entry = ttk.Entry(edit_window, width=30)
        amount_entry.insert(0, str(transaction['amount']))
        amount_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Item:").pack(pady=5)
        desc_entry = ttk.Entry(edit_window, width=30)
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
        
        ttk.Button(edit_window, text="Save", command=save_edited_transaction, width=15).pack(pady=5)
        ttk.Button(edit_window, text="Delete", command=delete_single_transaction, width=15).pack(pady=5)
        ttk.Button(edit_window, text="Cancel", command=edit_window.destroy, width=15).pack(pady=5)
    
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