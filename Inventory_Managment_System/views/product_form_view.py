import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView

class ProductFormView(BaseView):
    """View for adding/editing a product"""
    
    def __init__(self, parent, controller, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        self.product_id = kwargs.pop('product_id', None)
        super().__init__(parent, controller, **kwargs)
    
    def _create_widgets(self):
        # Main container with padding
        self.main_container = ttk.Frame(self, padding=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Form frame
        form_frame = ttk.LabelFrame(
            self.main_container, 
            text=f"{'Edit' if self.is_edit else 'Add New'} Product",
            padding=15
        )
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        ttk.Label(form_frame, text="Product Name *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Description").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(form_frame, width=40, height=4)
        self.desc_text.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Category").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.category_var,
            values=["Electronics", "Clothing", "Food", "Office", "Other"],
            width=37
        )
        category_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Price and cost frame
        price_frame = ttk.Frame(form_frame)
        price_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(price_frame, text="Price *").pack(side=tk.LEFT, padx=5)
        self.price_var = tk.DoubleVar()
        ttk.Entry(price_frame, textvariable=self.price_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(price_frame, text="Cost *").pack(side=tk.LEFT, padx=5)
        self.cost_var = tk.DoubleVar()
        ttk.Entry(price_frame, textvariable=self.cost_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Quantity frame
        quantity_frame = ttk.Frame(form_frame)
        quantity_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(quantity_frame, text="Current Quantity *").pack(side=tk.LEFT, padx=5)
        self.quantity_var = tk.IntVar()
        ttk.Entry(quantity_frame, textvariable=self.quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(quantity_frame, text="Minimum Quantity *").pack(side=tk.LEFT, padx=5)
        self.min_quantity_var = tk.IntVar(value=10)
        ttk.Entry(quantity_frame, textvariable=self.min_quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save", 
            style='Accent.TButton',
            command=self._on_save
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.controller.show_products
        ).pack(side=tk.LEFT, padx=10)
        
        # Set focus to name field
        name_entry.focus()
        
        # If editing, load the product data
        if self.is_edit and self.product_id:
            self.controller.load_product(self.product_id)
    
    def set_product_data(self, product_data):
        """Populate the form with product data"""
        self.name_var.set(product_data.get('name', ''))
        self.desc_text.delete('1.0', tk.END)
        self.desc_text.insert('1.0', product_data.get('description', ''))
        self.category_var.set(product_data.get('category', ''))
        self.price_var.set(product_data.get('price', 0.0))
        self.cost_var.set(product_data.get('cost', 0.0))
        self.quantity_var.set(product_data.get('quantity', 0))
        self.min_quantity_var.set(product_data.get('min_quantity', 10))
    
    def get_form_data(self):
        """Get the form data as a dictionary"""
        return {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get('1.0', tk.END).strip(),
            'category': self.category_var.get().strip(),
            'price': self.price_var.get(),
            'cost': self.cost_var.get(),
            'quantity': self.quantity_var.get(),
            'min_quantity': self.min_quantity_var.get()
        }
    
    def _on_save(self):
        """Handle save button click"""
        form_data = self.get_form_data()
        
        # Validate form
        if not form_data['name']:
            messagebox.showerror("Error", "Product name is required!")
            return
            
        if form_data['price'] <= 0:
            messagebox.showerror("Error", "Price must be greater than 0!")
            return
            
        if form_data['cost'] < 0:
            messagebox.showerror("Error", "Cost cannot be negative!")
            return
            
        if form_data['quantity'] < 0:
            messagebox.showerror("Error", "Quantity cannot be negative!")
            return
            
        if form_data['min_quantity'] < 0:
            messagebox.showerror("Error", "Minimum quantity cannot be negative!")
            return
        
        # Save the product
        if self.is_edit and self.product_id:
            self.controller.update_product(self.product_id, form_data)
        else:
            self.controller.add_product(form_data)
