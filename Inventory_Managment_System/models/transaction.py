from datetime import datetime
from models.base_model import BaseModel

class Transaction(BaseModel):
    """Transaction model for inventory movements"""
    
    _table_name = 'transactions'
    _fields = [
        'id', 'product_id', 'transaction_type', 'quantity', 
        'unit_price', 'total_price', 'notes', 'created_at'
    ]
    
    def __init__(self, **kwargs):
        # Set default values
        defaults = {
            'quantity': 0,
            'unit_price': 0.0,
            'total_price': 0.0,
            'created_at': datetime.now()
        }
        
        # Update defaults with provided values
        defaults.update(kwargs)
        
        # Calculate total price if not provided
        if 'total_price' not in kwargs and 'unit_price' in kwargs and 'quantity' in kwargs:
            defaults['total_price'] = float(kwargs['unit_price']) * int(kwargs['quantity'])
            
        super().__init__(**defaults)
    
    @classmethod
    def get_by_product(cls, product_id):
        """Get all transactions for a specific product"""
        db = Database()
        query = """
            SELECT t.*, p.name as product_name 
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            WHERE t.product_id = ?
            ORDER BY t.created_at DESC
        """
        return [cls(**dict(row)) for row in db.execute_query(query, (product_id,))]
    
    @classmethod
    def get_recent(cls, limit=50):
        """Get recent transactions across all products"""
        db = Database()
        query = """
            SELECT t.*, p.name as product_name 
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            ORDER BY t.created_at DESC
            LIMIT ?
        """
        return [cls(**dict(row)) for row in db.execute_query(query, (limit,))]
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': getattr(self, 'product_name', None),
            'transaction_type': self.transaction_type,
            'quantity': int(self.quantity),
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'notes': self.notes,
            'created_at': self.created_at
        }

# Import here to avoid circular imports
from database import Database
