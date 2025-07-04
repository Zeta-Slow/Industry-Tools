import tkinter as tk
from tkinter import ttk
from views.base_view import BaseView

class DashboardView(BaseView):
    """Dashboard view showing summary and quick actions"""
    
    def _create_widgets(self):
        # Main container
        self.main_container = ttk.Frame(self, padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text="Dashboard", 
            style='Header.TLabel',
            font=('Helvetica', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.main_container, text="Inventory Overview", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Stats cards
        self.total_items_var = tk.StringVar(value="0")
        self.low_stock_var = tk.StringVar(value="0")
        self.out_of_stock_var = tk.StringVar(value="0")
        
        self._create_stat_card(stats_frame, "Total Items", self.total_items_var, 0, 0)
        self._create_stat_card(stats_frame, "Low Stock", self.low_stock_var, 0, 1)
        self._create_stat_card(stats_frame, "Out of Stock", self.out_of_stock_var, 0, 2)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(self.main_container, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        # Activity list
        columns = ('date', 'type', 'product', 'qty', 'user')
        self.activity_tree = ttk.Treeview(
            activity_frame, 
            columns=columns, 
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.activity_tree.heading('date', text='Date/Time')
        self.activity_tree.heading('type', text='Type')
        self.activity_tree.heading('product', text='Product')
        self.activity_tree.heading('qty', text='Qty')
        self.activity_tree.heading('user', text='User')
        
        self.activity_tree.column('date', width=150)
        self.activity_tree.column('type', width=80, anchor=tk.CENTER)
        self.activity_tree.column('product', width=200)
        self.activity_tree.column('qty', width=60, anchor=tk.CENTER)
        self.activity_tree.column('user', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscroll=scrollbar.set)
        
        # Grid layout
        self.activity_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        activity_frame.grid_rowconfigure(0, weight=1)
        activity_frame.grid_columnconfigure(0, weight=1)
        
        # Quick actions frame
        actions_frame = ttk.Frame(self.main_container)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Action buttons
        ttk.Button(
            actions_frame, 
            text="New Product", 
            command=self.controller.show_add_product
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame, 
            text="Stock In", 
            command=self.controller.show_stock_in
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame, 
            text="Stock Out", 
            command=self.controller.show_stock_out
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame, 
            text="Generate Report", 
            command=self.controller.generate_report
        ).pack(side=tk.LEFT, padx=5)
    
    def _create_stat_card(self, parent, title, value_var, row, column):
        """Helper method to create a stat card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.grid(row=row, column=column, padx=10, pady=10, sticky='nsew')
        
        ttk.Label(
            card, 
            text=title,
            style='Subtitle.TLabel'
        ).pack(pady=(10, 5))
        
        ttk.Label(
            card, 
            textvariable=value_var,
            font=('Helvetica', 24, 'bold')
        ).pack(pady=(0, 10))
        
        # Configure grid weights
        parent.columnconfigure(column, weight=1)
        
        return card
    
    def update_stats(self, stats):
        """Update the dashboard statistics"""
        self.total_items_var.set(stats.get('total_items', 0))
        self.low_stock_var.set(stats.get('low_stock', 0))
        self.out_of_stock_var.set(stats.get('out_of_stock', 0))
    
    def update_activity(self, activities):
        """Update the recent activities list"""
        # Clear existing items
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Add new items
        for activity in activities:
            self.activity_tree.insert('', 'end', values=(
                activity.get('date', ''),
                activity.get('type', ''),
                activity.get('product', ''),
                activity.get('quantity', ''),
                activity.get('user', '')
            ))
