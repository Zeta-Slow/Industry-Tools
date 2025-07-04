import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController

def main():
    root = tk.Tk()
    root.title("Inventory Management System")
    root.geometry("1200x700")
    
    # Set window icon and style
    try:
        root.iconbitmap("assets/icon.ico")
    except:
        pass  # Icon file not found, use default
    
    # Initialize the main controller
    app = MainController(root)
    
    # Make the window resizable
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
