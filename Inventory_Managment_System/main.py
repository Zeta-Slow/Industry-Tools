import tkinter as tk
from tkinter import ttk
from views.main_view import MainView
from controllers.inventory_controller import InventoryController

def main():
    # Create main window
    root = tk.Tk()
    root.title("Sistema de Gestión de Inventario")
    root.geometry("1200x700")
    
    # Set window icon
    try:
        root.iconbitmap("assets/icon.ico")
    except:
        pass  # Icon file not found, use default
    
    # Configure styles
    style = ttk.Style()
    style.configure('Treeview', rowheight=25)
    style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
    
    # Create view
    view = MainView(root)
    
    # Create and initialize controller with view
    controller = InventoryController(view)
    
    # Pack the view
    view.pack(fill=tk.BOTH, expand=True)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
