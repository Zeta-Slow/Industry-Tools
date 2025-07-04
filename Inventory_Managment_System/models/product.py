from datetime import datetime
from models.base_model import BaseModel

class Product(BaseModel):
    """Product model for inventory management"""
    
    _table_name = 'products'
    _fields = [
        'id', 'name', 'description', 'category', 'price', 
        'cost', 'quantity', 'min_quantity', 'created_at', 'updated_at'
    ]
    
    def __init__(self, **kwargs):
        # Set default values
        defaults = {
            'price': 0.0,
            'cost': 0.0,
            'quantity': 0,
            'min_quantity': 10,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Update defaults with provided values
        defaults.update(kwargs)
        super().__init__(**defaults)
    
    def add_stock(self, quantity, unit_price, notes=None):
        """Add stock to the product"""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
            
        self.quantity += quantity
        self.save()
        
        # Record the transaction
        from models.transaction import Transaction
        transaction = Transaction(
            product_id=self.id,
            transaction_type='IN',
            quantity=quantity,
            unit_price=unit_price,
            total_price=quantity * unit_price,
            notes=notes
        )
        transaction.save()
    
    def remove_stock(self, quantity, unit_price=None, notes=None):
        """Remove stock from the product"""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
            
        if quantity > self.quantity:
            raise ValueError("Insufficient stock")
            
        self.quantity -= quantity
        self.save()
        
        # Record the transaction if unit_price is provided
        if unit_price is not None:
            from models.transaction import Transaction
            transaction = Transaction(
                product_id=self.id,
                transaction_type='OUT',
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price,
                notes=notes
            )
            transaction.save()
    
    def needs_restock(self):
        """Check if the product needs to be restocked"""
        return self.quantity <= self.min_quantity
    
    def get_low_stock_products(cls, threshold=None):
        """Get all products with quantity at or below their minimum quantity"""
        db = Database()
        if threshold is None:
            query = "SELECT * FROM products WHERE quantity <= min_quantity"
            results = db.execute_query(query)
        else:
            query = "SELECT * FROM products WHERE quantity <= ?"
            results = db.execute_query(query, (threshold,))
            
        return [cls(**dict(row)) for row in results]
    
    def get_transactions(self):
        """Get all transactions for this product"""
        from models.transaction import Transaction
        return Transaction.get_by_product(self.id)
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': float(self.price) if hasattr(self, 'price') else 0.0,
            'cost': float(self.cost) if hasattr(self, 'cost') else 0.0,
            'quantity': int(self.quantity) if hasattr(self, 'quantity') else 0,
            'min_quantity': int(self.min_quantity) if hasattr(self, 'min_quantity') else 0,
            'created_at': self.created_at if hasattr(self, 'created_at') else None,
            'updated_at': self.updated_at if hasattr(self, 'updated_at') else None
        }
