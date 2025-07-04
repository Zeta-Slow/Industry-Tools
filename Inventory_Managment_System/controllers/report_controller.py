import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from typing import List, Dict, Optional
from database import Database

class ReportController:
    """Controller for report generation"""
    
    def __init__(self):
        pass
    
    def generate_inventory_report(self, parts: List[Dict]) -> str:
        """Generate PDF inventory report"""
        if not parts:
            raise ValueError("No hay datos de inventario para generar el reporte")
        
        # Calculate report data
        total_parts = len(parts)
        total_value = sum(p.get('current_stock', 0) * p.get('unit_cost', 0) for p in parts)
        low_stock = [p for p in parts if p.get('current_stock', 0) < p.get('min_stock', 1)]
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Reporte de Inventario', 0, 1, 'C')
        pdf.ln(10)
        
        # Report info
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
        pdf.cell(0, 10, f'Total de partes: {total_parts}', 0, 1)
        pdf.cell(0, 10, f'Valor total del inventario: ${total_value:,.2f}', 0, 1)
        pdf.ln(10)
        
        # Low stock section
        if low_stock:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Partes con bajo stock:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            for part in low_stock:
                pdf.cell(0, 10, 
                        f"{part.get('part_number')} - {part.get('description')} | "
                        f"Stock: {part.get('current_stock')} (Mínimo: {part.get('min_stock')})", 
                        0, 1)
        else:
            pdf.cell(0, 10, '¡Todo el inventario está al día!', 0, 1)
        
        # Generate cost optimization chart
        chart_path = self._generate_cost_chart(parts)
        if chart_path and os.path.exists(chart_path):
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Análisis de costos:', 0, 1)
            pdf.image(chart_path, x=10, y=30, w=180)
            
            # Clean up chart file
            try:
                os.remove(chart_path)
            except:
                pass
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/inventario_{timestamp}.pdf"
        pdf.output(filename)
        
        return filename
    
    def generate_transaction_report(self, transactions: List[Dict]) -> str:
        """Generate PDF transaction report"""
        if not transactions:
            raise ValueError("No hay transacciones para generar el reporte")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Reporte de Transacciones', 0, 1, 'C')
        pdf.ln(10)
        
        # Report info
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
        pdf.cell(0, 10, f'Total de transacciones: {len(transactions)}', 0, 1)
        pdf.ln(10)
        
        # Transactions table
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Fecha', 1)
        pdf.cell(30, 10, 'Tipo', 1)
        pdf.cell(50, 10, 'Número de Parte', 1)
        pdf.cell(30, 10, 'Cantidad', 1)
        pdf.cell(30, 10, 'Precio', 1, 1)
        
        pdf.set_font('Arial', '', 10)
        for tx in transactions:
            pdf.cell(30, 10, str(tx.get('created_at', '')), 1)
            pdf.cell(30, 10, tx.get('transaction_type', ''), 1)
            pdf.cell(50, 10, tx.get('part_number', ''), 1)
            pdf.cell(30, 10, str(tx.get('quantity', '')), 1)
            pdf.cell(30, 10, f"${tx.get('unit_price', 0):.2f}", 1, 1)
        
        # Save report
        os.makedirs('reports', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/transacciones_{timestamp}.pdf"
        pdf.output(filename)
        
        return filename
    
    def _generate_cost_chart(self, parts: List[Dict]) -> Optional[str]:
        """Generate cost optimization chart and return file path"""
        try:
            if not parts:
                return None
                
            # Prepare data
            df = pd.DataFrame(parts)
            df['total_value'] = df['current_stock'] * df['unit_cost']
            df = df.sort_values('total_value', ascending=False).head(10)  # Top 10 items by value
            
            if df.empty:
                return None
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Bar chart
            bars = plt.bar(
                df['part_number'],
                df['total_value'],
                color='#3498db',
                alpha=0.7
            )
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + max(df['total_value']) * 0.01,
                    f'${height:,.2f}',
                    ha='center',
                    va='bottom',
                    rotation=45
                )
            
            # Customize plot
            plt.title('Top 10 Partes por Valor de Inventario', fontsize=14, pad=20)
            plt.xlabel('Número de Parte', fontsize=12)
            plt.ylabel('Valor Total ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save plot
            os.makedirs('temp', exist_ok=True)
            chart_path = 'temp/cost_chart.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"Error generating chart: {str(e)}")
            return None
