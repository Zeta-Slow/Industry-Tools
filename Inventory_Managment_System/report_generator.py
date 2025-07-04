from fpdf import FPDF
from datetime import datetime
import os

class ReportGenerator:
    """Class for generating PDF reports"""
    
    def __init__(self):
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_inventory_report(self, products, title="Inventory Report"):
        """Generate an inventory report PDF"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # Date
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.ln(5)
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        col_widths = [15, 60, 30, 25, 25, 25, 25]
        headers = ['ID', 'Product', 'Category', 'Qty', 'Min Qty', 'Price', 'Status']
        
        # Header row
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()
        
        # Table rows
        pdf.set_font('Arial', '', 10)
        for product in products:
            # Determine status
            quantity = product.get('quantity', 0)
            min_quantity = product.get('min_quantity', 0)
            
            if quantity <= 0:
                status = 'Out of Stock'
            elif quantity <= min_quantity:
                status = 'Low Stock'
            else:
                status = 'In Stock'
            
            # Add row
            pdf.cell(col_widths[0], 10, str(product.get('id', '')), 'LR', 0, 'C')
            pdf.cell(col_widths[1], 10, product.get('name', '')[:30], 'LR', 0, 'L')
            pdf.cell(col_widths[2], 10, product.get('category', '')[:15], 'LR', 0, 'L')
            pdf.cell(col_widths[3], 10, str(quantity), 'LR', 0, 'C')
            pdf.cell(col_widths[4], 10, str(min_quantity), 'LR', 0, 'C')
            pdf.cell(col_widths[5], 10, f"${product.get('price', 0):.2f}", 'LR', 0, 'R')
            pdf.cell(col_widths[6], 10, status, 'LR', 0, 'C')
            pdf.ln()
        
        # Close table
        pdf.cell(sum(col_widths), 0, '', 'T')
        
        # Add summary
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Summary', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        total_products = len(products)
        out_of_stock = len([p for p in products if p.get('quantity', 0) <= 0])
        low_stock = len([p for p in products if 0 < p.get('quantity', 0) <= p.get('min_quantity', 0)])
        
        pdf.cell(0, 8, f"Total Products: {total_products}", 0, 1)
        pdf.cell(0, 8, f"Out of Stock: {out_of_stock}", 0, 1)
        pdf.cell(0, 8, f"Low Stock: {low_stock}", 0, 1)
        
        # Save the report
        filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.report_dir, filename)
        pdf.output(filepath)
        
        return filepath
    
    def generate_transaction_report(self, transactions, title="Transaction Report"):
        """Generate a transaction report PDF"""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # Date
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.ln(5)
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        col_widths = [25, 25, 70, 20, 25, 25]
        headers = ['Date', 'Type', 'Product', 'Qty', 'Unit Price', 'Total']
        
        # Header row
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()
        
        # Table rows
        pdf.set_font('Arial', '', 10)
        total_in = 0
        total_out = 0
        
        for tx in transactions:
            # Calculate totals
            amount = float(tx.get('quantity', 0)) * float(tx.get('unit_price', 0))
            
            if tx.get('type') == 'IN':
                total_in += amount
            else:
                total_out += amount
            
            # Add row
            pdf.cell(col_widths[0], 10, str(tx.get('date', '')), 'LR', 0, 'C')
            pdf.cell(col_widths[1], 10, str(tx.get('type', '')), 'LR', 0, 'C')
            pdf.cell(col_widths[2], 10, str(tx.get('product', ''))[:35], 'LR', 0, 'L')
            pdf.cell(col_widths[3], 10, str(tx.get('quantity', '')), 'LR', 0, 'C')
            pdf.cell(col_widths[4], 10, f"${float(tx.get('unit_price', 0)):.2f}", 'LR', 0, 'R')
            pdf.cell(col_widths[5], 10, f"${amount:.2f}", 'LR', 0, 'R')
            pdf.ln()
        
        # Close table
        pdf.cell(sum(col_widths), 0, '', 'T')
        
        # Add summary
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Summary', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Total Transactions: {len(transactions)}", 0, 1)
        pdf.cell(0, 8, f"Total Stock In: ${total_in:.2f}", 0, 1)
        pdf.cell(0, 8, f"Total Stock Out: ${total_out:.2f}", 0, 1)
        pdf.cell(0, 8, f"Net: ${total_in - total_out:.2f}", 0, 1)
        
        # Save the report
        filename = f"transaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.report_dir, filename)
        pdf.output(filepath)
        
        return filepath
