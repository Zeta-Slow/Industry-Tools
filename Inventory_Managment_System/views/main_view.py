import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
from datetime import datetime
import os

class MainView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None
        self.handlers = {}
        self.style = ttk.Style()
        
        # Configure colors
        self.colors = {
            'primary': '#2c3e50',     # Dark blue
            'secondary': '#ecf0f1',   # Light gray
            'accent': '#3498db',      # Blue
            'background': '#ffffff',  # White
            'text': '#2c3e50',        # Dark gray/blue
            'danger': '#e74c3c'       # Red for delete buttons
        }
        
        self._setup_styles()
        self._create_ui()
    
    def _setup_styles(self):
        """Configure ttk styles"""
        self.style.theme_use('clam')
        
        # Configure main frame
        self.style.configure('TFrame', background=self.colors['background'])
        
        # Configure buttons
        self.style.configure('TButton',
                           padding=6,
                           font=('Segoe UI', 9))
                           
        self.style.map('TButton',
                     foreground=[('active', self.colors['text'])],
                     background=[('active', self.colors['secondary'])])
        
        # Configure treeview
        self.style.configure('Treeview',
                           fieldbackground=self.colors['background'],
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           rowheight=25,
                           borderwidth=0)
                           
        self.style.configure('Treeview.Heading',
                           background=self.colors['primary'],
                           foreground='white',
                           padding=5,
                           font=('Segoe UI', 9, 'bold'))
                           
        self.style.map('Treeview',
                     background=[('selected', self.colors['accent'])],
                     foreground=[('selected', 'white')])
        
        # Configure entry
        self.style.configure('TEntry',
                           fieldbackground='white',
                           padding=5)
    
    def _create_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_search_bar()
        self._create_treeview()
        self._create_status_bar()
        
        # Bind events
        self._bind_events()
    
    def add_handlers(self, handlers):
        """Set up event handlers from controller"""
        self.handlers = handlers
        
    def _bind_events(self):
        """Bind UI events to handler methods"""
        # Bind double click to edit
        self.tree.bind('<Double-1>', lambda e: self._handle_event('on_edit'))
        
    def _handle_event(self, event_name, *args, **kwargs):
        """Handle UI events by calling the appropriate handler"""
        handler = self.handlers.get(event_name)
        if handler and callable(handler):
            return handler(*args, **kwargs)
    
    def _create_menu_bar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportar a Excel", command=lambda: self._handle_event('on_export'))
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.master.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        # Inventory menu
        inventory_menu = tk.Menu(menubar, tearoff=0)
        inventory_menu.add_command(label="Añadir Parte", command=lambda: self._handle_event('on_add'))
        inventory_menu.add_command(label="Editar Parte", command=lambda: self._handle_event('on_edit'))
        inventory_menu.add_command(label="Eliminar Parte", command=lambda: self._handle_event('on_delete'))
        menubar.add_cascade(label="Inventario", menu=inventory_menu)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Reporte de Inventario", 
                               command=lambda: self._handle_event('on_generate_report', 'inventory'))
        reports_menu.add_command(label="Reporte de Transacciones", 
                               command=lambda: self._handle_event('on_generate_report', 'transactions'))
        menubar.add_cascade(label="Reportes", menu=reports_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
    
    def _create_toolbar(self):
        toolbar = ttk.Frame(self, style='Toolbar.TFrame')
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Toolbar buttons
        add_btn = ttk.Button(toolbar, text="Añadir", 
                           command=lambda: self._handle_event('on_add'),
                           style='Toolbutton.TButton')
        add_btn.pack(side='left', padx=2)
        
        edit_btn = ttk.Button(toolbar, text="Editar",
                            command=lambda: self._handle_event('on_edit'),
                            style='Toolbutton.TButton')
        edit_btn.pack(side='left', padx=2)
        
        delete_btn = ttk.Button(toolbar, text="Eliminar",
                              command=lambda: self._handle_event('on_delete'),
                              style='Danger.TButton')
        delete_btn.pack(side='left', padx=2)
        
        separator = ttk.Separator(toolbar, orient='vertical')
        separator.pack(side='left', fill='y', padx=5)
        
        report_btn = ttk.Button(toolbar, text="Generar Reporte",
                              command=lambda: self._handle_event('on_generate_report', 'inventory'),
                              style='Toolbutton.TButton')
        report_btn.pack(side='left', padx=2)
    
    def _create_search_bar(self):
        search_frame = ttk.Frame(self)
        search_frame.grid(row=1, column=0, sticky='new', padx=5, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', padx=(0, 5))
        
        search_btn = ttk.Button(search_frame, text="Buscar",
                              command=self.on_search_click)
        search_btn.pack(side='left')
        
        clear_btn = ttk.Button(search_frame, text="Limpiar",
                             command=self.clear_search)
        clear_btn.pack(side='left', padx=5)
    
    def _create_treeview(self):
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
        
        # Create scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'part_number', 'description', 'category', 'current_stock', 'unit_cost'),
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            selectmode='browse',
            show='headings'
        )
        
        # Configure scrollbars
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading('id', text='ID', anchor='w')
        self.tree.heading('part_number', text='Número de Parte', anchor='w')
        self.tree.heading('description', text='Descripción', anchor='w')
        self.tree.heading('category', text='Categoría', anchor='w')
        self.tree.heading('current_stock', text='Stock Actual', anchor='center')
        self.tree.heading('unit_cost', text='Costo Unitario', anchor='e')
        
        # Configure column widths
        self.tree.column('id', width=50, minwidth=50, stretch=False)
        self.tree.column('part_number', width=150, minwidth=100)
        self.tree.column('description', width=250, minwidth=150)
        self.tree.column('category', width=120, minwidth=100)
        self.tree.column('current_stock', width=100, minwidth=80, anchor='center')
        self.tree.column('unit_cost', width=120, minwidth=100, anchor='e')
        
        # Add tag for low stock
        self.tree.tag_configure('low_stock', background='#fff3cd')
        self.tree.tag_configure('out_of_stock', background='#f8d7da')
        
        # Grid the treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double click to edit
        self.tree.bind('<Double-1>', lambda e: self.controller.edit_selected_part())
    
    def _create_status_bar(self):
        status_bar = ttk.Frame(self, style='StatusBar.TFrame')
        status_bar.grid(row=3, column=0, sticky='ew')
        
        self.status_var = tk.StringVar()
        self.status_var.set('Listo')
        
        status_label = ttk.Label(status_bar, textvariable=self.status_var)
        status_label.pack(side='left', padx=5)
        
        # Add item count
        self.item_count_var = tk.StringVar()
        self.item_count_var.set('0 elementos')
        
        count_label = ttk.Label(status_bar, textvariable=self.item_count_var)
        count_label.pack(side='right', padx=5)
    
    def update_parts_list(self, items):
        """Update the treeview with the provided items"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for item in items:
            values = (
                item.get('id'),
                item.get('part_number', ''),
                item.get('description', ''),
                item.get('category', ''),
                item.get('current_stock', 0),
                f"${item.get('unit_cost', 0):.2f}"
            )
            
            # Check stock status
            tags = ()
            if item.get('current_stock', 0) <= 0:
                tags = ('out_of_stock',)
            elif item.get('current_stock', 0) < item.get('min_stock', 0):
                tags = ('low_stock',)
                
            self.tree.insert('', 'end', values=values, tags=tags)
        
        # Update item count
        self.item_count_var.set(f"{len(items)} elementos")
    
    def get_selected_part(self):
        """Get the currently selected part"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        # Get the selected item's values
        item = self.tree.item(selection[0])
        if not item or 'values' not in item or len(item['values']) < 6:
            return None
            
        # Map values to part dictionary
        part = {
            'id': item['values'][0],
            'part_number': item['values'][1],
            'description': item['values'][2],
            'category': item['values'][3],
            'current_stock': item['values'][4],
            'unit_cost': float(item['values'][5].replace('$', '')),
            'min_stock': 0  # Default value, can be updated if needed
        }
        return part
    
    def show_part_form(self, part_data=None):
        """Show the part form dialog"""
        form = PartForm(self, part_data)
        result = form.show()
        if result:
            self._handle_event('on_save_part', result)
    
    def ask_confirmation(self, title, message):
        """Show a confirmation dialog"""
        return messagebox.askyesno(title, message)
    
    def show_error(self, title, message):
        """Show an error message"""
        messagebox.showerror(title, message)
    
    def show_info(self, title, message):
        """Show an info message"""
        messagebox.showinfo(title, message)
    
    def get_selected_item(self):
        """Get the currently selected item in the treeview"""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0])['values']
    
    def on_search(self, *args):
        """Handle search as user types"""
        search_term = self.search_var.get().lower()
        self._handle_event('on_search', search_term)
    
    def on_search_click(self):
        """Handle search button click"""
        self.on_search()
    
    def clear_search(self):
        """Clear the search field"""
        self.search_var.set('')
        self._handle_event('on_search', '')
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Sistema de Gestión de Inventario

Versión: 1.0.0

© 2025 Industrias ACME
Todos los derechos reservados."""
        messagebox.showinfo("Acerca de", about_text)
    
    def show_error(self, title, message):
        """Show error message"""
        messagebox.showerror(title, message)
    
    def ask_confirmation(self, title, message):
        """Show confirmation dialog"""
        return messagebox.askyesno(title, message)


class PartForm(tk.Toplevel):
    def __init__(self, parent, controller, part_data=None):
        super().__init__(parent)
        self.controller = controller
        self.part_data = part_data or {}
        
        self.title("Añadir/Editar Parte" if not part_data else "Editar Parte")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Make the window modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        self._create_widgets()
        
        # Focus on the first field
        if not part_data:
            self.part_number_entry.focus_set()
    
    def _create_widgets(self):
        # Main container
        container = ttk.Frame(self, padding="20")
        container.pack(fill='both', expand=True)
        
        # Form fields
        ttk.Label(container, text="Número de Parte:").grid(row=0, column=0, sticky='w', pady=5)
        self.part_number_var = tk.StringVar(value=self.part_data.get('part_number', ''))
        self.part_number_entry = ttk.Entry(container, textvariable=self.part_number_var, width=40)
        self.part_number_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Descripción:").grid(row=1, column=0, sticky='w', pady=5)
        self.description_var = tk.StringVar(value=self.part_data.get('description', ''))
        ttk.Entry(container, textvariable=self.description_var, width=40).grid(
            row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Categoría:").grid(row=2, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar(value=self.part_data.get('category', ''))
        category_combo = ttk.Combobox(
            container,
            textvariable=self.category_var,
            values=["Eléctrico", "Mecánico", "Neumático", "Hidráulico", "Otros"],
            state='readonly',
            width=37
        )
        category_combo.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Stock Actual:").grid(row=3, column=0, sticky='w', pady=5)
        self.stock_var = tk.StringVar(value=str(self.part_data.get('current_stock', 0)))
        ttk.Spinbox(
            container,
            from_=0,
            to=10000,
            textvariable=self.stock_var,
            width=10
        ).grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Stock Mínimo:").grid(row=4, column=0, sticky='w', pady=5)
        self.min_stock_var = tk.StringVar(value=str(self.part_data.get('min_stock', 0)))
        ttk.Spinbox(
            container,
            from_=0,
            to=10000,
            textvariable=self.min_stock_var,
            width=10
        ).grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Costo Unitario:").grid(row=5, column=0, sticky='w', pady=5)
        self.cost_var = tk.StringVar(value=str(self.part_data.get('unit_cost', 0.0)))
        ttk.Entry(container, textvariable=self.cost_var, width=20).grid(
            row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Label(container, text="Proveedor:").grid(row=6, column=0, sticky='w', pady=5)
        self.supplier_var = tk.StringVar(value=self.part_data.get('supplier', ''))
        ttk.Entry(container, textvariable=self.supplier_var, width=40).grid(
            row=6, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="Aceptar",
            command=self.on_accept,
            style='Accent.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side='right')
        
        # Configure grid weights
        container.columnconfigure(1, weight=1)
    
    def on_accept(self):
        """Handle accept button click"""
        try:
            # Validate fields
            if not self.part_number_var.get().strip():
                raise ValueError("El número de parte es obligatorio")
                
            part_data = {
                'part_number': self.part_number_var.get().strip(),
                'description': self.description_var.get().strip(),
                'category': self.category_var.get(),
                'current_stock': int(self.stock_var.get()),
                'min_stock': int(self.min_stock_var.get()),
                'unit_cost': float(self.cost_var.get() or 0),
                'supplier': self.supplier_var.get().strip()
            }
            
            # If editing existing part, include the ID
            if 'id' in self.part_data:
                part_data['id'] = self.part_data['id']
            
            self.controller.save_part(part_data)
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
    
    def show(self):
        """Show the form and wait for it to be closed"""
        self.wait_window()
        return self.result
