# Inventory Management System

A desktop application for managing inventory built with Python and Tkinter.

## Features

- **Product Management**: Add, edit, delete, and view products
- **Stock Control**: Track stock levels with minimum quantity alerts
- **Transactions**: Record stock in/out movements
- **Reports**: Generate PDF reports for inventory and transactions
- **Database**: SQLite database for data persistence
- **Responsive UI**: Works on different screen resolutions (720p, 1080p)

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- See `requirements.txt` for additional dependencies

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Inventory_Managment_System
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Building the Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

The executable will be created in the `dist` directory.

## Project Structure

```
Inventory_Managment_System/
├── controllers/           # Application controllers
│   ├── __init__.py
│   └── main_controller.py
├── models/               # Database models
│   ├── __init__.py
│   ├── base_model.py
│   ├── product.py
│   └── transaction.py
├── views/                # UI views
│   ├── __init__.py
│   ├── base_view.py
│   ├── dashboard_view.py
│   ├── product_view.py
│   ├── product_form_view.py
│   └── stock_movement_view.py
├── data/                 # Database storage
│   └── inventory.db
├── reports/              # Generated reports
├── assets/               # Images, icons, etc.
│   └── icon.ico
├── database.py           # Database connection
├── report_generator.py   # PDF report generation
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
