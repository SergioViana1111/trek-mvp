from fpdf import FPDF
import os

class ContractPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'ADITIVO AO CONTRATO DE LOCAÇÃO DE EQUIPAMENTO', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_contract_pdf(user_data, product_data, company_data):
    pdf = ContractPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # 1. Preamble
    pdf.multi_cell(0, 5, 
        "Este documento refere-se ao ADITIVO do Contrato-Mãe de Locação de Equipamentos "
        "firmado entre a LOCADORA e a EMPRESA parceira. O LOCATÁRIO abaixo qualificado adere "
        "integralmente aos termos do Contrato-Mãe ao assinar este Aditivo.")
    pdf.ln(5)
    
    # 2. Parties
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "1. DADOS DO LOCATÁRIO (COLABORADOR)", 0, 1)
    pdf.set_font("Arial", size=10)
    
    pdf.cell(40, 6, f"Nome:", 0, 0)
    pdf.cell(0, 6, f"{user_data.get('name')}", 0, 1)
    
    pdf.cell(40, 6, f"CPF:", 0, 0)
    pdf.cell(0, 6, f"{user_data.get('cpf')}", 0, 1)
    
    pdf.cell(40, 6, f"E-mail:", 0, 0)
    pdf.cell(0, 6, f"{user_data.get('email')}", 0, 1)
    
    pdf.cell(40, 6, f"Celular:", 0, 0)
    pdf.cell(0, 6, f"{user_data.get('phone')}", 0, 1)
    
    pdf.cell(40, 6, f"Endereço:", 0, 0)
    pdf.multi_cell(0, 6, f"{user_data.get('address')}")
    pdf.ln(5)
    
    # 3. Object
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "2. EQUIPAMENTO LOCADO", 0, 1)
    pdf.set_font("Arial", size=10)
    
    pdf.cell(40, 6, "Marca/Modelo:", 0, 0)
    pdf.cell(0, 6, f"{product_data.get('brand')} {product_data.get('model')}", 0, 1)
    
    pdf.cell(40, 6, "Descrição:", 0, 0)
    pdf.multi_cell(0, 6, f"{product_data.get('description')}")
    
    # IMEI
    pdf.cell(40, 6, "IMEI:", 0, 0)
    imei = product_data.get('imei')
    if imei:
        pdf.cell(0, 6, f"{imei}", 0, 1)
    else:
        pdf.cell(0, 6, "___________________________________ (Preenchido na Expedição)", 0, 1)
    pdf.ln(5)
    
    # 4. Values
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "3. VALORES E CONDIÇÕES", 0, 1)
    pdf.set_font("Arial", size=10)
    
    pdf.cell(50, 6, "Valor da Assinatura Mensal:", 0, 0)
    pdf.cell(0, 6, f"R$ {product_data.get('monthly_price')}", 0, 1)
    
    pdf.cell(50, 6, "Valor do Seguro Mensal:", 0, 0)
    pdf.cell(0, 6, f"R$ {product_data.get('insurance_price')}", 0, 1)
    
    pdf.cell(50, 6, "Valor Residual (Opção de Compra):", 0, 0)
    pdf.cell(0, 6, f"R$ {product_data.get('residual_value')}", 0, 1)
    pdf.ln(5)
    
    # 5. Acceptance
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "4. ACEITE DIGITAL", 0, 1)
    pdf.set_font("Arial", size=10)
    
    acceptance_date = user_data.get('acceptance_date', 'N/A')
    pdf.multi_cell(0, 5, 
        f"O LOCATÁRIO declara que LEU E CONCORDOU com os termos do Contrato-Mãe e este Aditivo "
        f"em {acceptance_date}, através de confirmação eletrônica via sistema TREK.")
    
    pdf.ln(10)
    pdf.cell(0, 10, "."*60, 0, 1, 'C')
    pdf.cell(0, 5, "Assinatura Eletrônica Registrada", 0, 1, 'C')

    # Save
    filename = f"aditivo_{user_data.get('cpf')}_{product_data.get('model')}.pdf"
    # Cleanup filename spaces
    filename = filename.replace(" ", "_").replace("/", "-")
    
    # If using Streamlit cloud, might want to save to tmp or similar. 
    # For local/MVP, current dir is fine.
    try:
        pdf.output(filename)
    except Exception as e:
        # Fallback if permission issue
        filename = "aditivo_temp.pdf"
        pdf.output(filename)
        
    return filename
