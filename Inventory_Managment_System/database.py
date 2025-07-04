import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union

class Database:
    def __init__(self, db_path: str = 'data/inventory.db'):
        """Initialize database connection and create tables if they don't exist."""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def _create_tables(self) -> None:
        """Create the necessary tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create parts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_number TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT,
                    current_stock INTEGER NOT NULL DEFAULT 0,
                    min_stock INTEGER NOT NULL DEFAULT 0,
                    unit_cost REAL NOT NULL DEFAULT 0.0,
                    supplier TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create transactions table for audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,  -- 'IN' or 'OUT'
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    reference TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (part_id) REFERENCES parts (id)
                )
            ''')
            
            # Create trigger to update updated_at timestamp
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_part_timestamp
                AFTER UPDATE ON parts
                BEGIN
                    UPDATE parts SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = OLD.id;
                END;
            ''')
            
            conn.commit()
    
    # CRUD Operations for Parts
    
    def insert_part(self, part_data: Dict[str, Union[str, int, float]]) -> int:
        """
        Insert a new part into the database.
        
        Args:
            part_data: Dictionary containing part information with keys:
                      - part_number (str): Unique part number
                      - description (str, optional): Part description
                      - category (str, optional): Part category
                      - current_stock (int, optional): Current stock level, defaults to 0
                      - min_stock (int, optional): Minimum stock level, defaults to 0
                      - unit_cost (float, optional): Cost per unit, defaults to 0.0
                      - supplier (str, optional): Supplier information
        
        Returns:
            int: The ID of the newly inserted part
        """
        required_fields = ['part_number']
        for field in required_fields:
            if field not in part_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default values for optional fields
        defaults = {
            'current_stock': 0,
            'min_stock': 0,
            'unit_cost': 0.0,
            'description': '',
            'category': '',
            'supplier': ''
        }
        
        # Merge defaults with provided data
        part_data = {**defaults, **part_data}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO parts (
                        part_number, description, category, 
                        current_stock, min_stock, unit_cost, supplier
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    part_data['part_number'],
                    part_data['description'],
                    part_data['category'],
                    part_data['current_stock'],
                    part_data['min_stock'],
                    part_data['unit_cost'],
                    part_data['supplier']
                ))
                part_id = cursor.lastrowid
                
                # Record the initial stock transaction
                if part_data['current_stock'] > 0:
                    self._record_transaction(
                        part_id=part_id,
                        transaction_type='IN',
                        quantity=part_data['current_stock'],
                        unit_price=part_data['unit_cost'],
                        reference='INITIAL',
                        notes='Initial stock'
                    )
                
                conn.commit()
                return part_id
                
            except sqlite3.IntegrityError as e:
                if 'UNIQUE' in str(e):
                    raise ValueError(f"Part number '{part_data['part_number']}' already exists") from e
                raise
    
    def update_part(self, part_id: int, update_data: Dict[str, Union[str, int, float]]) -> bool:
        """
        Update an existing part.
        
        Args:
            part_id: The ID of the part to update
            update_data: Dictionary containing fields to update
            
        Returns:
            bool: True if update was successful, False if part not found
        """
        if not update_data:
            return False
            
        set_clause = ', '.join(f"{key} = ?" for key in update_data.keys())
        values = list(update_data.values())
        values.append(part_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE parts 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            
            if cursor.rowcount == 0:
                return False
                
            conn.commit()
            return True
    
    def delete_part(self, part_id: int) -> bool:
        """
        Delete a part from the database.
        
        Args:
            part_id: The ID of the part to delete
            
        Returns:
            bool: True if deletion was successful, False if part not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # First, delete related transactions
            cursor.execute('DELETE FROM transactions WHERE part_id = ?', (part_id,))
            
            # Then delete the part
            cursor.execute('DELETE FROM parts WHERE id = ?', (part_id,))
            rows_affected = cursor.rowcount
            
            conn.commit()
            return rows_affected > 0
    
    def get_part(self, part_id: int) -> Optional[Dict]:
        """
        Retrieve a part by its ID.
        
        Args:
            part_id: The ID of the part to retrieve
            
        Returns:
            Optional[Dict]: The part data as a dictionary, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM parts WHERE id = ?', (part_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_part_by_number(self, part_number: str) -> Optional[Dict]:
        """
        Retrieve a part by its part number.
        
        Args:
            part_number: The part number to search for
            
        Returns:
            Optional[Dict]: The part data as a dictionary, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM parts WHERE part_number = ?', (part_number,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_parts(self, category: str = None) -> List[Dict]:
        """
        Retrieve all parts, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List[Dict]: List of parts as dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute('SELECT * FROM parts WHERE category = ? ORDER BY part_number', (category,))
            else:
                cursor.execute('SELECT * FROM parts ORDER BY part_number')
                
            return [dict(row) for row in cursor.fetchall()]
    
    def get_low_stock(self, threshold: int = None) -> List[Dict]:
        """
        Retrieve parts with stock levels below their minimum threshold.
        
        Args:
            threshold: Optional override for the minimum stock level
            
        Returns:
            List[Dict]: List of parts that are below their minimum stock level
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if threshold is not None:
                cursor.execute('''
                    SELECT * FROM parts 
                    WHERE current_stock < ?
                    ORDER BY current_stock ASC
                ''', (threshold,))
            else:
                cursor.execute('''
                    SELECT * FROM parts 
                    WHERE current_stock < min_stock
                    ORDER BY current_stock ASC
                ''')
                
            return [dict(row) for row in cursor.fetchall()]
    
    # Transaction Management
    
    def _record_transaction(
        self,
        part_id: int,
        transaction_type: str,
        quantity: int,
        unit_price: float,
        reference: str = None,
        notes: str = None
    ) -> int:
        """
        Record a stock transaction (internal use).
        
        Args:
            part_id: The ID of the part
            transaction_type: Either 'IN' or 'OUT'
            quantity: Number of units
            unit_price: Price per unit
            reference: Optional reference number/ID
            notes: Optional notes about the transaction
            
        Returns:
            int: The ID of the created transaction
        """
        if transaction_type not in ('IN', 'OUT'):
            raise ValueError("Transaction type must be 'IN' or 'OUT'")
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (
                    part_id, transaction_type, quantity, 
                    unit_price, reference, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                part_id, transaction_type, quantity,
                unit_price, reference, notes
            ))
            
            transaction_id = cursor.lastrowid
            
            # Update the part's stock level
            if transaction_type == 'IN':
                cursor.execute('''
                    UPDATE parts 
                    SET current_stock = current_stock + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantity, part_id))
            else:  # OUT
                cursor.execute('''
                    UPDATE parts 
                    SET current_stock = current_stock - ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantity, part_id))
            
            conn.commit()
            return transaction_id
    
    def stock_in(
        self,
        part_id: int,
        quantity: int,
        unit_price: float,
        reference: str = None,
        notes: str = None
    ) -> int:
        """
        Record a stock increase transaction.
        
        Args:
            part_id: The ID of the part
            quantity: Number of units to add
            unit_price: Price per unit
            reference: Optional reference number/ID
            notes: Optional notes about the transaction
            
        Returns:
            int: The ID of the created transaction
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
            
        return self._record_transaction(
            part_id=part_id,
            transaction_type='IN',
            quantity=quantity,
            unit_price=unit_price,
            reference=reference,
            notes=notes
        )
    
    def stock_out(
        self,
        part_id: int,
        quantity: int,
        unit_price: float = None,
        reference: str = None,
        notes: str = None
    ) -> int:
        """
        Record a stock decrease transaction.
        
        Args:
            part_id: The ID of the part
            quantity: Number of units to remove
            unit_price: Optional price per unit (for sales/valuation)
            reference: Optional reference number/ID
            notes: Optional notes about the transaction
            
        Returns:
            int: The ID of the created transaction
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
            
        # If unit_price is not provided, use the part's current unit_cost
        if unit_price is None:
            part = self.get_part(part_id)
            if not part:
                raise ValueError(f"Part with ID {part_id} not found")
            unit_price = part['unit_cost']
            
        return self._record_transaction(
            part_id=part_id,
            transaction_type='OUT',
            quantity=quantity,
            unit_price=unit_price,
            reference=reference,
            notes=notes
        )
    
    def get_part_transactions(
        self,
        part_id: int,
        limit: int = None,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Retrieve transactions for a specific part.
        
        Args:
            part_id: The ID of the part
            limit: Optional limit on number of transactions to return
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            List[Dict]: List of transaction records
        """
        query = '''
            SELECT t.*, p.part_number, p.description 
            FROM transactions t
            JOIN parts p ON t.part_id = p.id
            WHERE t.part_id = ?
        '''
        params = [part_id]
        
        # Add date filters if provided
        if start_date:
            query += ' AND DATE(t.created_at) >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND DATE(t.created_at) <= ?'
            params.append(end_date)
            
        query += ' ORDER BY t.created_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_transactions(
        self,
        limit: int = 100,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Retrieve all transactions with part information.
        
        Args:
            limit: Maximum number of transactions to return
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            List[Dict]: List of transaction records with part details
        """
        query = '''
            SELECT t.*, p.part_number, p.description 
            FROM transactions t
            JOIN parts p ON t.part_id = p.id
        '''
        params = []
        
        # Add date filters if provided
        conditions = []
        if start_date:
            conditions.append('DATE(t.created_at) >= ?')
            params.append(start_date)
        if end_date:
            conditions.append('DATE(t.created_at) <= ?')
            params.append(end_date)
            
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        query += ' ORDER BY t.created_at DESC LIMIT ?'
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

# Example usage
if __name__ == '__main__':
    # Initialize the database
    db = Database('inventory.db')
    
    # Example: Insert a new part
    part_id = db.insert_part({
        'part_number': 'RES-1K',
        'description': '1K Ohm Resistor',
        'category': 'Electronics',
        'current_stock': 100,
        'min_stock': 50,
        'unit_cost': 0.10,
        'supplier': 'ElectroParts Inc.'
    })
    print(f"Inserted part with ID: {part_id}")
    
    # Example: Get all parts
    parts = db.get_all_parts()
    print("\nAll parts:")
    for part in parts:
        print(f"{part['id']}: {part['part_number']} - {part['description']} ({part['current_stock']} in stock)")
    
    # Example: Record a stock in transaction
    db.stock_in(
        part_id=part_id,
        quantity=50,
        unit_price=0.12,
        reference='PO12345',
        notes='Monthly restock'
    )
    
    # Example: Get low stock items
    low_stock = db.get_low_stock()
    print("\nLow stock items:")
    for item in low_stock:
        print(f"{item['part_number']}: {item['current_stock']} (min: {item['min_stock']})")
    
    # Example: Get transaction history
    transactions = db.get_part_transactions(part_id)
    print("\nTransaction history:")
    for tx in transactions:
        print(f"{tx['created_at']}: {tx['transaction_type']} {tx['quantity']} units at ${tx['unit_price']:.2f} each")

import sqlite3
import os
from datetime import datetime

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.db_path = os.path.join(os.path.dirname(__file__), 'data', 'inventory.db')
            self._create_tables()
            self._initialized = True
    
    def get_connection(self):
        """Get a database connection"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    price REAL NOT NULL,
                    cost REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    min_quantity INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    transaction_type TEXT CHECK(transaction_type IN ('IN', 'OUT')),
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Create triggers for auto-updating timestamps
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_products_timestamp
                AFTER UPDATE ON products
                BEGIN
                    UPDATE products SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = OLD.id;
                END;
            ''')
            
            conn.commit()
    
    def execute_query(self, query, params=(), fetch_one=False, fetch_all=True, commit=False):
        """Execute a SQL query with parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if commit:
                conn.commit()
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            
            return cursor.lastrowid
