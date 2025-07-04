import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from views.base_view import BaseView

class StockMovementView(BaseView):
    """View for handling stock in/out operations"""
    
    def __init__(self, parent, controller, movement_type='in', product_id=None, **kwargs):
        self.movement_type = movement_type  # 'in' or 'out'
        self.product_id = product_id
        super().__init__(parent, controller, **kwargs)
    
    def _create_widgets(self):
        # Main container with padding
        self.main_container = ttk.Frame(self, padding=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Form frame
        form_frame = ttk.LabelFrame(
            self.main_container, 
            text=f"Stock {'In' if self.movement_type == 'in' else 'Out'}",
            padding=15
        )
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product selection (if not pre-selected)
        if not self.product_id:
            ttk.Label(form_frame, text="Product *").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.product_var = tk.StringVar()
            self.product_combo = ttk.Combobox(
                form_frame, 
                textvariable=self.product_var,
                width=40,
                state='readonly'
            )
            self.product_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
            self.product_combo.bind('<<ComboboxSelected>>', self._on_product_selected)
            
            # Load products
            self.controller.load_products_for_selection()
        else:
            # If product is pre-selected, show product info
            self.product_info_frame = ttk.LabelFrame(form_frame, text="Product Information", padding=10)
            self.product_info_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=5)
            
            self.product_name_var = tk.StringVar()
            self.current_stock_var = tk.StringVar()
            
            ttk.Label(self.product_info_frame, text="Product:").grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.product_info_frame, textvariable=self.product_name_var).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
            
            ttk.Label(self.product_info_frame, text="Current Stock:").grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(self.product_info_frame, textvariable=self.current_stock_var).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
            
            # Load product data
            self.controller.load_product_for_movement(self.product_id)
        
        # Quantity
        ttk.Label(form_frame, text=f"Quantity *").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(form_frame, textvariable=self.quantity_var, width=15)
        self.quantity_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.quantity_entry.focus()
        
        # Unit Price (for stock in) or Selling Price (for stock out)
        if self.movement_type == 'in':
            price_label = "Unit Price *"
        else:
            price_label = "Selling Price *"
            
        ttk.Label(form_frame, text=price_label).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.price_var, width=15).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Reference/Notes
        ttk.Label(form_frame, text="Reference/Notes").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(form_frame, width=40, height=4)
        self.notes_text.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Date
        ttk.Label(form_frame, text="Date").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.date_var, width=12).pack(side=tk.LEFT, padx=2)
        
        self.time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))
        ttk.Entry(date_frame, textvariable=self.time_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text=f"Process Stock {'In' if self.movement_type == 'in' else 'Out'}", 
            style='Accent.TButton',
            command=self._on_process
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.controller.show_products
        ).pack(side=tk.LEFT, padx=10)
    
    def set_products_list(self, products):
        """Set the list of products in the combobox"""
        if hasattr(self, 'product_combo'):
            self.products = products
            self.product_combo['values'] = [p['name'] for p in products]
    
    def set_product_data(self, product_data):
        """Set the product data in the form"""
        if hasattr(self, 'product_name_var'):
            self.product_name_var.set(product_data.get('name', ''))
            self.current_stock_var.set(f"{product_data.get('quantity', 0)} units")
            
            # Set default price based on movement type
            if self.movement_type == 'in':
                self.price_var.set(product_data.get('cost', 0.0))
            else:
                self.price_var.set(product_data.get('price', 0.0))
    
    def _on_product_selected(self, event=None):
        """Handle product selection from combobox"""
        selected_idx = self.product_combo.current()
        if selected_idx >= 0 and hasattr(self, 'products'):
            product = self.products[selected_idx]
            self.product_id = product['id']
            self.set_product_data(product)
    
    def _on_process(self):
        """Handle process button click"""
        # Validate form
        if not self.product_id:
            messagebox.showerror("Error", "Please select a product!")
            return
            
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid quantity!")
            return
            
        try:
            price = float(self.price_var.get())
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid price!")
            return
        
        # Prepare transaction data
        transaction_data = {
            'product_id': self.product_id,
            'quantity': quantity,
            'unit_price': price,
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'transaction_date': f"{self.date_var.get()} {self.time_var.get()}"
        }
        
        # Process the stock movement
        if self.movement_type == 'in':
            self.controller.process_stock_in(transaction_data)
        else:
            self.controller.process_stock_out(transaction_data)
