from fpdf import FPDF
import os

class ContractPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'CONTRATO DE LOCAÇÃO DE EQUIPAMENTO', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_contract_pdf(user_data, product_data, company_data):
    pdf = ContractPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Content
    content = [
        f"LOCADOR: Trek Soluções",
        f"LOCATÁRIO: {user_data.get('name')}, CPF: {user_data.get('cpf')}",
        f"EMPRESA: {company_data.get('name')}, CNPJ: {company_data.get('cnpj')}",
        "",
        "OBJETO DO CONTRATO:",
        f"Aparelho: {product_data.get('brand')} {product_data.get('model')}",
        f"Valor Mensal: R$ {product_data.get('monthly_price')}",
        "",
        "CLÁUSULAS:",
        "1. O equipamento deve ser devolvido em boas condições.",
        "2. O seguro cobre roubo e furto qualificado mediante BO.",
        "",
        "ACEITE DIGITAL:",
        f"Assinado eletronicamente por {user_data.get('name')}",
        # In real app, add timestamp and IP here
    ]
    
    for line in content:
        pdf.cell(0, 10, line, 0, 1)

    # Save to temp file
    output_path = f"contract_{user_data.get('cpf')}.pdf"
    pdf.output(output_path)
    return output_path
