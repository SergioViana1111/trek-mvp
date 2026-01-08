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

def generate_contract_pdf(contract_data, product_data, company_data):
    """
    Generates the Aditivo PDF with specific closed scope fields.
    
    contract_data expects:
    - name, cpf, address, email, phone
    - start_date, end_date, months
    - value_monthly_total, residual_value
    
    product_data expects:
    - brand, model, description, imei (optional)
    """
    pdf = ContractPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # 1. Dados do Assinante
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "1. DADOS DO ASSINANTE", 0, 1)
    pdf.set_font("Arial", size=10)
    
    fields_subscriber = [
        ("Nome", contract_data.get('name')),
        ("CPF", contract_data.get('cpf')),
        ("Endereço", contract_data.get('address')),
        ("Celular", contract_data.get('phone')),
        ("E-mail", contract_data.get('email'))
    ]
    
    for label, value in fields_subscriber:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 6, f"{label}:", 0, 0)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, f"{value if value else ''}")
    
    pdf.ln(5)
    
    # 2. Dados do Aparelho
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "2. DADOS DO APARELHO", 0, 1)
    
    fields_device = [
        ("Marca", product_data.get('brand')),
        ("Modelo", product_data.get('model')),
        ("Descrição", product_data.get('description')),
        ("IMEI", product_data.get('imei') if product_data.get('imei') else "___________________________________")
    ]
    
    for label, value in fields_device:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 6, f"{label}:", 0, 0)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, f"{value if value else ''}")
        
    pdf.ln(5)

    # 3. Dados da Contratação
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "3. DADOS DA CONTRATAÇÃO", 0, 1)
    
    val_monthly = contract_data.get('value_monthly_total')
    try:
        val_monthly_fmt = f"R$ {float(val_monthly):.2f}"
    except:
        val_monthly_fmt = str(val_monthly)

    val_residual = contract_data.get('residual_value')
    try:
        val_residual_fmt = f"R$ {float(val_residual):.2f}"
    except:
        val_residual_fmt = str(val_residual)

    fields_contract = [
        ("Data de Início", contract_data.get('start_date')),
        ("Data Final", contract_data.get('end_date')),
        ("Qtd. Meses", str(contract_data.get('months'))),
        ("Valor (c/ Seg)", val_monthly_fmt),
        ("Valor Residual", val_residual_fmt)
    ]
    
    for label, value in fields_contract:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 6, f"{label}:", 0, 0)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, f"{value}")
        
    pdf.ln(10)
    
    # Acceptance Text
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, 
        "Ao asssinar este documento, o Assinante declara que leu e concorda com todos os termos do Contrato-Mãe. "
        "Este documento foi gerado eletronicamente após validação de aceite digital.")
        
    pdf.ln(10)
    pdf.cell(0, 5, "."*50, 0, 1, 'C')
    pdf.cell(0, 5, "Assinatura Digital - TREK", 0, 1, 'C')

    # Save
    filename = f"aditivo_{contract_data.get('cpf')}_{product_data.get('model')}.pdf"
    filename = filename.replace(" ", "_").replace("/", "-")
    
    try:
        pdf.output(filename)
    except:
        filename = "aditivo_temp.pdf"
        pdf.output(filename)
        
    return filename
