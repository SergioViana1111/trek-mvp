import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.pdf_service import generate_contract_pdf
import time

st.set_page_config(page_title="Trek - Contrato", page_icon="📝")

require_auth()

if "selected_product" not in st.session_state:
    st.warning("Nenhum aparelho selecionado.")
    st.stop()

product = st.session_state["selected_product"]
user = st.session_state["user"]
# Fetch company info for the user
supabase = get_supabase()
company = {}
try:
    res = supabase.table("companies").select("*").eq("id", user["company_id"]).execute()
    if res.data:
        company = res.data[0]
except:
    pass

st.title("Assinatura do Contrato")
st.success(f"Você escolheu: **{product['brand']} {product['model']}**")

st.markdown("### Endereço de Entrega")
col_cep, col_num = st.columns([1, 1])
with col_cep:
    cep = st.text_input("CEP")
with col_num:
    number = st.text_input("Número")
    
street = st.text_input("Logradouro (Rua/Av)")
complement = st.text_input("Complemento")

st.markdown("### Termos e Condições")
st.markdown("Lorem ipsum dolor sit amet... (Texto do contrato aqui)")

# Contract Preview or Checkbox
agree = st.checkbox("Declaro que li e concordo com os termos do contrato de locação.")

if st.button("Assinar e Confirmar Pedido"):
    if not (cep and number and street):
        st.error("Por favor, preencha o endereço de entrega.")
    elif agree:
        with st.spinner("Gerando contrato..."):
            # Generate PDF
            pdf_path = generate_contract_pdf(user, product, company)
            
            # Upload PDF to Storage (omitted for MVP speed, simulating URL)
            # In real app: upload to bucket, get public url
            contract_url = "https://fake-url.com/contract.pdf"
            
            # Create Order
            order_data = {
                "user_id": user["id"],
                "product_id": product["id"],
                "company_id": user["company_id"],
                "status": "contract_signed",
                "contract_url": contract_url,
                "signed_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "delivery_address": {
                    "cep": cep,
                    "street": street,
                    "number": number, 
                    "complement": complement
                }
            }
            
            supabase.table("orders").insert(order_data).execute()
            
            # Send Email
            from services.email_service import send_email
            email_subject = "Seu Contrato Trek - Assinado"
            email_body = f"Olá {user['name']},\n\nSeu contrato para o aparelho {product['brand']} {product['model']} foi assinado com sucesso.\n\nContrato: {contract_url}"
            send_email(user.get("email"), email_subject, email_body, pdf_path)
            
            st.success("Contrato assinado com sucesso! Seu pedido foi gerado.")
            st.balloons()
            st.info("Você receberá o contrato por e-mail.")
            
            # Generate WhatsApp Link
            # Format: https://wa.me/?text=...
            msg_text = f"Olá, acabei de assinar o contrato do meu {product['brand']} {product['model']}. Segue o link: {contract_url}"
            import urllib.parse
            encoded_text = urllib.parse.quote(msg_text)
            wa_link = f"https://wa.me/?text={encoded_text}"
            
            st.markdown(f"""
            <a href="{wa_link}" target="_blank">
                <button style="
                    background-color:#25D366; 
                    color:white; 
                    border:none; 
                    padding:10px 20px; 
                    border-radius:5px; 
                    font-weight:bold; 
                    cursor:pointer;">
                    📱 Enviar comprovante por WhatsApp
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            # Cleanup
            del st.session_state["selected_product"]
            time.sleep(10) # Give more time to click link
            st.switch_page("app.py")
    else:
        st.error("Você precisa aceitar os termos para continuar.")
