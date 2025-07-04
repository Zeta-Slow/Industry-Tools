import tkinter as tk
from tkinter import ttk, messagebox
from views.dashboard_view import DashboardView
from views.product_view import ProductView
from views.product_form_view import ProductFormView
from views.stock_movement_view import StockMovementView
from models.product import Product
from models.transaction import Transaction

class MainController:
    """Main controller for the application"""
    
    def __init__(self, root):
        self.root = root
        self.current_view = None
        self._setup_ui()
        self.show_dashboard()
    
    def _setup_ui(self):
        """Set up the main UI components"""
        # Configure window
        self.root.minsize(1000, 600)
        self.root.title("Inventory Management System")
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self._create_sidebar()
        
        # Create content area
        self.content_area = ttk.Frame(self.main_container)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def _create_sidebar(self):
        """Create the sidebar navigation"""
        sidebar = ttk.Frame(self.main_container, width=200, style='Sidebar.TFrame')
        sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        
        # Logo/Title
        ttk.Label(
            sidebar, 
            text="IMS", 
            style='Sidebar.TLabel',
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(20, 30), padx=10)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Products", self.show_products),
            ("Categories", self.show_categories),
            ("Transactions", self.show_transactions),
            ("Reports", self.show_reports),
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(
                sidebar, 
                text=text,
                style='Sidebar.TButton',
                command=command
            )
            btn.pack(fill=tk.X, padx=10, pady=2)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(sidebar)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            bottom_frame,
            text="Settings",
            command=self.show_settings
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            bottom_frame,
            text="Exit",
            command=self.root.quit
        ).pack(fill=tk.X, pady=2)
        
        # Configure styles
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure the style of the sidebar
        style.configure('Sidebar.TFrame', background='#f0f0f0')
        style.configure('Sidebar.TLabel', background='#f0f0f0')
        
        # Configure sidebar buttons
        style.configure('Sidebar.TButton', 
                      anchor="w", 
                      padding=10,
                      font=('Helvetica', 10))
        
        # Hover effect for sidebar buttons
        style.map('Sidebar.TButton',
                 background=[('active', '#e0e0e0')])
        
        # Accent button style
        style.configure('Accent.TButton',
                      font=('Helvetica', 10, 'bold'),
                      padding=8)
    
    def _switch_view(self, view_class, *args, **kwargs):
        """Switch to a new view"""
        # Clear current view
        if self.current_view:
            self.current_view.destroy()
        
        # Create and pack new view
        self.current_view = view_class(self.content_area, self, *args, **kwargs)
        self.current_view.pack(fill=tk.BOTH, expand=True)
    
    # Navigation methods
    def show_dashboard(self):
        """Show the dashboard view"""
        self._switch_view(DashboardView)
        self._update_dashboard()
    
    def show_products(self):
        """Show the products view"""
        self._switch_view(ProductView)
        self._update_products_list()
    
    def show_add_product(self):
        """Show the add product form"""
        self._switch_view(ProductFormView, is_edit=False)
    
    def show_edit_product(self, product_id):
        """Show the edit product form"""
        self._switch_view(ProductFormView, is_edit=True, product_id=product_id)
    
    def show_stock_in(self, product_id=None):
        """Show the stock in form"""
        self._switch_view(StockMovementView, movement_type='in', product_id=product_id)
    
    def show_stock_out(self, product_id=None):
        """Show the stock out form"""
        self._switch_view(StockMovementView, movement_type='out', product_id=product_id)
    
    def show_categories(self):
        """Show categories view (not implemented)"""
        messagebox.showinfo("Info", "Categories management will be implemented in a future update.")
    
    def show_transactions(self):
        """Show transactions view (not implemented)"""
        messagebox.showinfo("Info", "Transaction history will be implemented in a future update.")
    
    def show_reports(self):
        """Show reports view (not implemented)"""
        messagebox.showinfo("Info", "Reports will be implemented in a future update.")
    
    def show_settings(self):
        """Show settings view (not implemented)"""
        messagebox.showinfo("Info", "Settings will be implemented in a future update.")
    
    # Data methods
    def _update_dashboard(self):
        """Update dashboard with current data"""
        # Get product stats
        total_products = Product.get_all()
        low_stock = [p for p in total_products if p.quantity <= p.min_quantity and p.quantity > 0]
        out_of_stock = [p for p in total_products if p.quantity <= 0]
        
        stats = {
            'total_items': len(total_products),
            'low_stock': len(low_stock),
            'out_of_stock': len(out_of_stock)
        }
        
        # Get recent activities
        recent_transactions = Transaction.get_recent(10)
        activities = [{
            'date': t.created_at,
            'type': 'Stock In' if t.transaction_type == 'IN' else 'Stock Out',
            'product': t.product_name,
            'quantity': t.quantity,
            'user': 'System'  # In a real app, this would be the current user
        } for t in recent_transactions]
        
        # Update the dashboard view
        if isinstance(self.current_view, DashboardView):
            self.current_view.update_stats(stats)
            self.current_view.update_activity(activities)
    
    def _update_products_list(self):
        """Update the products list in the products view"""
        if not isinstance(self.current_view, ProductView):
            return
            
        products = Product.get_all()
        self.current_view.update_products([p.to_dict() for p in products])
    
    def load_product(self, product_id):
        """Load product data into the form"""
        product = Product.get_by_id(product_id)
        if product and isinstance(self.current_view, ProductFormView):
            self.current_view.set_product_data(product.to_dict())
    
    def add_product(self, product_data):
        """Add a new product"""
        try:
            product = Product(**product_data)
            product.save()
            messagebox.showinfo("Success", "Product added successfully!")
            self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def update_product(self, product_id, product_data):
        """Update an existing product"""
        try:
            product = Product.get_by_id(product_id)
            if product:
                for key, value in product_data.items():
                    setattr(product, key, value)
                product.save()
                messagebox.showinfo("Success", "Product updated successfully!")
                self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            product = Product.get_by_id(product_id)
            if product:
                product.delete()
                self._update_products_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
    
    def load_products_for_selection(self):
        """Load products for selection in stock movement forms"""
        if not isinstance(self.current_view, StockMovementView):
            return
            
        products = Product.get_all()
        self.current_view.set_products_list([p.to_dict() for p in products])
    
    def load_product_for_movement(self, product_id):
        """Load product data for stock movement"""
        if not isinstance(self.current_view, StockMovementView):
            return
            
        product = Product.get_by_id(product_id)
        if product:
            self.current_view.set_product_data(product.to_dict())
    
    def process_stock_in(self, transaction_data):
        """Process a stock in transaction"""
        try:
            product = Product.get_by_id(transaction_data['product_id'])
            if product:
                product.add_stock(
                    transaction_data['quantity'],
                    transaction_data['unit_price'],
                    transaction_data.get('notes')
                )
                messagebox.showinfo("Success", "Stock added successfully!")
                self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process stock in: {str(e)}")
    
    def process_stock_out(self, transaction_data):
        """Process a stock out transaction"""
        try:
            product = Product.get_by_id(transaction_data['product_id'])
            if product:
                product.remove_stock(
                    transaction_data['quantity'],
                    transaction_data['unit_price'],
                    transaction_data.get('notes')
                )
                messagebox.showinfo("Success", "Stock removed successfully!")
                self.show_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process stock out: {str(e)}")
    
    def generate_report(self):
        """Generate a report (not implemented)"""
        messagebox.showinfo("Info", "Report generation will be implemented in a future update.")
