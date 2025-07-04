import tkinter as tk
from tkinter import ttk

class BaseView(ttk.Frame):
    """Base view class that provides common functionality for all views"""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.parent = parent
        self.style = ttk.Style()
        self._setup_styles()
        self._create_widgets()
    
    def _setup_styles(self):
        """Configure ttk styles"""
        # Configure the style of the Treeview
        style = ttk.Style()
        style.configure("Treeview",
                       rowheight=25,
                       fieldbackground="#ffffff")
        style.configure("Treeview.Heading",
                       font=('Helvetica', 10, 'bold'))
        style.map('Treeview', 
                 background=[('selected', '#0078d7')],
                 foreground=[('selected', 'white')])
        
        # Configure button styles
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('Header.TLabel', 
                       font=('Helvetica', 12, 'bold'),
                       padding=5)
        style.configure('Subtitle.TLabel',
                      font=('Helvetica', 10),
                      foreground='gray')
    
    def _create_widgets(self):
        """Create the widgets for the view"""
        # This method should be overridden by subclasses
        pass
    
    def show_info(self, title, message):
        """Show an info message dialog"""
        tk.messagebox.showinfo(title, message)
    
    def show_error(self, title, message):
        """Show an error message dialog"""
        tk.messagebox.showerror(title, message)
    
    def ask_yesno(self, title, message):
        """Show a yes/no confirmation dialog"""
        return tk.messagebox.askyesno(title, message)
    
    def clear_frame(self):
        """Clear all widgets from the frame"""
        for widget in self.winfo_children():
            widget.destroy()
    
    def on_show(self, **kwargs):
        """Called when the view is shown"""
        # This method can be overridden by subclasses
        pass
