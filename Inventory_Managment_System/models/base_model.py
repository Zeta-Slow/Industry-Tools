from database import Database

class BaseModel:
    """Base model class that provides common database operations"""
    
    _table_name = None
    _fields = []
    
    def __init__(self, **kwargs):
        self.db = Database()
        for field in self._fields:
            setattr(self, field, kwargs.get(field, None))
    
    @classmethod
    def get_all(cls):
        """Get all records from the table"""
        db = Database()
        query = f"SELECT * FROM {cls._table_name}"
        return [cls(**dict(row)) for row in db.execute_query(query)]
    
    @classmethod
    def get_by_id(cls, id):
        """Get a single record by ID"""
        db = Database()
        query = f"SELECT * FROM {cls._table_name} WHERE id = ?"
        result = db.execute_query(query, (id,), fetch_one=True)
        return cls(**dict(result)) if result else None
    
    def save(self):
        """Save the current instance to the database"""
        if hasattr(self, 'id') and self.id is not None:
            self.update()
        else:
            self.create()
    
    def create(self):
        """Create a new record in the database"""
        fields = [f for f in self._fields if f != 'id' and hasattr(self, f) and getattr(self, f) is not None]
        placeholders = ', '.join(['?'] * len(fields))
        field_names = ', '.join(fields)
        values = [getattr(self, f) for f in fields]
        
        query = f"INSERT INTO {self._table_name} ({field_names}) VALUES ({placeholders})"
        self.id = self.db.execute_query(query, values, commit=True)
    
    def update(self):
        """Update an existing record in the database"""
        if not hasattr(self, 'id') or self.id is None:
            raise ValueError("Cannot update a record without an ID")
            
        fields = [f for f in self._fields if f != 'id' and hasattr(self, f)]
        set_clause = ', '.join([f"{f} = ?" for f in fields])
        values = [getattr(self, f) for f in fields]
        values.append(self.id)
        
        query = f"UPDATE {self._table_name} SET {set_clause} WHERE id = ?"
        self.db.execute_query(query, values, commit=True)
    
    def delete(self):
        """Delete the current record from the database"""
        if not hasattr(self, 'id') or self.id is None:
            raise ValueError("Cannot delete a record without an ID")
            
        query = f"DELETE FROM {self._table_name} WHERE id = ?"
        self.db.execute_query(query, (self.id,), commit=True)
        self.id = None
