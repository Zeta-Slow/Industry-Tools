import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
from database import Database
from views.main_view import PartForm
from .report_controller import ReportController

class InventoryController:
    """Controller for inventory management"""
    
    def __init__(self, view):
        self.view = view
        self.db = Database()
        self.current_parts = []
        self.filtered_parts = []
        self._setup_handlers()
        self.load_parts()
    
    def _setup_handlers(self):
        """Set up event handlers"""
        self.view.add_handlers({
            'on_add': self.show_add_part,
            'on_edit': self.edit_selected_part,
            'on_delete': self.delete_selected_part,
            'on_search': self.search_parts,
            'on_export': self.export_to_excel,
            'on_generate_report': self.generate_report,
            'on_save_part': self.save_part
        })
    
    def load_parts(self, search_term: str = None):
        """Load parts from the database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM parts ORDER BY part_number')
                self.current_parts = [dict(row) for row in cursor.fetchall()]
                self.filter_parts(search_term)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading parts: {str(e)}")
    
    def filter_parts(self, search_term: str = None):
        """Filter parts based on search term"""
        if not search_term:
            self.filtered_parts = self.current_parts
        else:
            search_term = search_term.lower()
            self.filtered_parts = [
                p for p in self.current_parts 
                if (search_term in str(p.get('part_number', '')).lower() or
                    search_term in str(p.get('description', '')).lower() or
                    search_term in str(p.get('category', '')).lower())
            ]
        self.view.update_parts_list(self.filtered_parts)
    
    def show_add_part(self):
        """Show add part dialog"""
        self.view.show_part_form()
    
    def edit_selected_part(self):
        """Edit selected part"""
        selected = self.view.get_selected_part()
        if not selected:
            return
            
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM parts WHERE id = ?', (selected['id'],))
                part_data = cursor.fetchone()
                
                if part_data:
                    part_data = dict(part_data)
                    self.view.show_part_form(part_data)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos de la parte: {str(e)}")
    
    def delete_selected_part(self):
        """Delete selected part after confirmation"""
        selected = self.view.get_selected_part()
        if not selected:
            return
            
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la parte '{selected.get('part_number')}'?"
        ):
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    # First delete related transactions
                    cursor.execute('DELETE FROM transactions WHERE part_id = ?', (selected['id'],))
                    # Then delete the part
                    cursor.execute('DELETE FROM parts WHERE id = ?', (selected['id'],))
                    conn.commit()
                    
                self.load_parts()
                messagebox.showinfo("Éxito", "Parte eliminada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la parte: {str(e)}")
    
    def save_part(self, part_data: dict) -> bool:
        """Save part to database"""
        try:
            # Validate required fields
            if not part_data.get('part_number'):
                messagebox.showerror("Error", "El número de parte es obligatorio")
                return False
            
            # Convert numeric fields
            try:
                part_data['current_stock'] = int(part_data.get('current_stock', 0))
                part_data['min_stock'] = int(part_data.get('min_stock', 0))
                part_data['unit_cost'] = float(part_data.get('unit_cost', 0))
            except (ValueError, TypeError) as e:
                messagebox.showerror("Error", "Los campos numéricos no son válidos")
                return False
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                if 'id' in part_data and part_data['id']:
                    # Update existing part
                    cursor.execute('''
                        UPDATE parts SET 
                            part_number = ?,
                            description = ?,
                            category = ?,
                            current_stock = ?,
                            min_stock = ?,
                            unit_cost = ?,
                            supplier = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (
                        part_data['part_number'],
                        part_data.get('description', ''),
                        part_data.get('category', ''),
                        part_data['current_stock'],
                        part_data['min_stock'],
                        part_data['unit_cost'],
                        part_data.get('supplier', ''),
                        part_data['id']
                    ))
                    message = "Parte actualizada correctamente"
                else:
                    # Insert new part
                    cursor.execute('''
                        INSERT INTO parts (
                            part_number, description, category, 
                            current_stock, min_stock, unit_cost, supplier
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        part_data['part_number'],
                        part_data.get('description', ''),
                        part_data.get('category', ''),
                        part_data['current_stock'],
                        part_data['min_stock'],
                        part_data['unit_cost'],
                        part_data.get('supplier', '')
                    ))
                    message = "Parte agregada correctamente"
                
                conn.commit()
                self.load_parts()
                messagebox.showinfo("Éxito", message)
                return True
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la parte: {str(e)}")
            return False
    
    def generate_report(self, report_type: str = 'inventory'):
        """Generate a report of the specified type"""
        try:
            os.makedirs('reports', exist_ok=True)
            report_controller = ReportController()
            
            if report_type == 'inventory':
                filename = report_controller.generate_inventory_report(self.current_parts)
                self.show_info("Reporte generado", f"Reporte guardado como: {filename}")
            elif report_type == 'transactions':
                transactions = self.db.get_all_transactions(limit=1000)
                filename = report_controller.generate_transaction_report(transactions)
                self.show_info("Reporte generado", f"Reporte de transacciones guardado como: {filename}")
                
        except Exception as e:
            self.show_error("Error", f"Error al generar el reporte: {str(e)}")
    
    def _export_to_csv(self, data, report_name):
        """Export data to CSV file"""
        if not data:
            messagebox.showinfo("Información", "No hay datos para exportar.")
            return
        
        try:
            import csv
            from datetime import datetime
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_name}_{timestamp}.csv"
            
            # Get fieldnames from the first item
            fieldnames = list(data[0].keys())
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            messagebox.showinfo("Éxito", f"Reporte exportado como: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")
    
    def export_to_excel(self):
        """Export current parts list to Excel"""
        try:
            if not self.filtered_parts:
                messagebox.showinfo("Información", "No hay datos para exportar")
                return
                
            # Create exports directory if it doesn't exist
            os.makedirs('exports', exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join('exports', f'inventario_{timestamp}.xlsx')
            
            # Create DataFrame and save to Excel
            df = pd.DataFrame(self.filtered_parts)
            df.to_excel(filename, index=False, engine='openpyxl')
            
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")
            return None
    
    def search_parts(self, search_term):
        """Search parts by the given term"""
        self.load_parts(search_term if search_term else None)

