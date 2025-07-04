import tkinter as tk
from tkinter import ttk, messagebox
from views.base_view import BaseView

class ProductView(BaseView):
    """View for managing products"""
    
    def _create_widgets(self):
        # Main container with padding
        self.main_container = ttk.Frame(self, padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with title and buttons
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text="Product Management", 
            style='Header.TLabel',
            font=('Helvetica', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # Action buttons frame
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame, 
            text="Add New Product",
            command=self.controller.show_add_product
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.controller.refresh_products
        ).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.main_container)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.focus()
        
        # Products table
        columns = ('id', 'name', 'category', 'quantity', 'price', 'status')
        self.tree = ttk.Treeview(
            self.main_container, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.tree.heading('id', text='ID', command=lambda: self._sort_column('id', False))
        self.tree.heading('name', text='Product Name', command=lambda: self._sort_column('name', False))
        self.tree.heading('category', text='Category', command=lambda: self._sort_column('category', False))
        self.tree.heading('quantity', text='Qty', command=lambda: self._sort_column('quantity', True))
        self.tree.heading('price', text='Price', command=lambda: self._sort_column('price', True))
        self.tree.heading('status', text='Status', command=lambda: self._sort_column('status', False))
        
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200)
        self.tree.column('category', width=150)
        self.tree.column('quantity', width=80, anchor=tk.CENTER)
        self.tree.column('price', width=100, anchor=tk.E)
        self.tree.column('status', width=120, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        # Configure grid weights
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self._on_view_details)
        self.context_menu.add_command(label="Edit Product", command=self._on_edit_product)
        self.context_menu.add_command(label="Delete Product", command=self._on_delete_product)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Stock In", command=self._on_stock_in)
        self.context_menu.add_command(label="Stock Out", command=self._on_stock_out)
        
        # Bind events
        self.tree.bind('<Button-3>', self._show_context_menu)
        self.tree.bind('<Double-1>', lambda e: self._on_view_details())
    
    def _sort_column(self, col, is_numeric):
        """Sort tree by column"""
        if not hasattr(self, '_sort_state'):
            self._sort_state = {}
        
        # Get current sort order
        current_sort = self._sort_state.get(col, 'asc')
        
        # Toggle sort order
        new_sort = 'desc' if current_sort == 'asc' else 'asc'
        self._sort_state[col] = new_sort
        
        # Get all items from the tree
        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Sort the items
        if is_numeric:
            items.sort(key=lambda t: float(t[0]) if t[0].replace('.', '').isdigit() else 0, 
                      reverse=(new_sort == 'desc'))
        else:
            items.sort(reverse=(new_sort == 'desc'))
        
        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)
        
        # Update heading with sort indicator
        for c in self.tree['columns']:
            self.tree.heading(c, text=c.capitalize())
        
        self.tree.heading(col, text=f"{col.capitalize()} {'▲' if new_sort == 'asc' else '▼'}")
    
    def _on_search(self, *args):
        """Handle search box changes"""
        search_term = self.search_var.get().lower()
        
        # If search is empty, show all items
        if not search_term:
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
                self.tree.detach(item)
                self.tree.reattach(item, '', 'end')
            return
        
        # Filter items
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if any(search_term in str(value).lower() for value in values):
                self.tree.item(item, tags=('match',))
                self.tree.detach(item)
                self.tree.attach('', item, 'end')
            else:
                self.tree.item(item, tags=())
    
    def _show_context_menu(self, event):
        """Show the context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _on_view_details(self, event=None):
        """Handle view details action"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            product_id = item['values'][0]  # Assuming ID is the first column
            self.controller.view_product_details(product_id)
    
    def _on_edit_product(self):
        """Handle edit product action"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            product_id = item['values'][0]  # Assuming ID is the first column
            self.controller.edit_product(product_id)
    
    def _on_delete_product(self):
        """Handle delete product action"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            product_id = item['values'][0]
            product_name = item['values'][1]
            
            if messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete '{product_name}'?\nThis action cannot be undone."
            ):
                self.controller.delete_product(product_id)
    
    def _on_stock_in(self):
        """Handle stock in action"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            product_id = item['values'][0]
            self.controller.stock_in(product_id)
    
    def _on_stock_out(self):
        """Handle stock out action"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            product_id = item['values'][0]
            self.controller.stock_out(product_id)
    
    def update_products(self, products):
        """Update the products list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for product in products:
            status = self._get_status(product)
            self.tree.insert('', 'end', values=(
                product.get('id'),
                product.get('name'),
                product.get('category', 'Uncategorized'),
                product.get('quantity', 0),
                f"${product.get('price', 0):.2f}",
                status
            ))
    
    def _get_status(self, product):
        """Get status text and color based on stock level"""
        quantity = product.get('quantity', 0)
        min_quantity = product.get('min_quantity', 0)
        
        if quantity <= 0:
            return 'Out of Stock'
        elif quantity <= min_quantity:
            return 'Low Stock'
        else:
            return 'In Stock'
