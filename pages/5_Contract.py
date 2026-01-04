import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.pdf_service import generate_contract_pdf
from services.cep_service import get_address_from_cep
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

# Function to handle CEP search
def search_cep():
    cep_input = st.session_state.get("cep_input", "")
    if cep_input:
        address = get_address_from_cep(cep_input)
        if address:
            st.session_state["street_input"] = address.get("street", "")
            st.session_state["neighborhood_input"] = address.get("neighborhood", "")
            # st.session_state["city_input"] = address.get("city", "") # If needed
            # st.session_state["state_input"] = address.get("state", "") # If needed
            st.toast("Endereço encontrado!", icon="✅")
        else:
            st.toast("CEP não encontrado.", icon="❌")

st.markdown("### Contato")
col_email, col_phone = st.columns(2)
with col_email:
    email = st.text_input("E-mail", value=user.get("email", ""), key="email_input")
with col_phone:
    phone = st.text_input("Celular", key="phone_input")

st.markdown("### Endereço de Entrega")
col_cep, col_btn_cep = st.columns([3, 1])
with col_cep:
    cep = st.text_input("CEP", key="cep_input")
with col_btn_cep:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Buscar CEP"):
        search_cep()
        st.rerun()

col_street, col_num = st.columns([3, 1])
with col_street:
    street = st.text_input("Logradouro (Rua/Av)", key="street_input")
with col_num:
    number = st.text_input("Número", key="number_input")
    
col_comp, col_neigh = st.columns(2)
with col_comp:
    complement = st.text_input("Complemento", key="complement_input")
with col_neigh:
    neighborhood = st.text_input("Bairro", key="neighborhood_input")

st.markdown("### Termos e Condições")
st.markdown("Lorem ipsum dolor sit amet... (Texto do contrato aqui)")

# Contract Preview or Checkbox
agree = st.checkbox("Declaro que li e concordo com os termos do contrato de locação.")

if st.button("Assinar e Confirmar Pedido"):
    if not (email and phone and cep and number and street):
        st.error("Por favor, preencha todos os campos obrigatórios (E-mail, Celular, Endereço).")
    elif agree:
        with st.spinner("Gerando contrato..."):
            # Generate PDF
            # Update user info with new contact details if needed, or just pass to contract
            contract_user_info = user.copy()
            contract_user_info["email"] = email
            contract_user_info["phone"] = phone
            
            pdf_path = generate_contract_pdf(contract_user_info, product, company)
            
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
                    "complement": complement,
                    "neighborhood": neighborhood
                },
                "contact_info": {
                    "email": email,
                    "phone": phone
                }
            }
            
            supabase.table("orders").insert(order_data).execute()
            
            # Send Email
            from services.email_service import send_email
            email_subject = "Seu Contrato Trek - Assinado"
            email_body = f"Olá {user['name']},\n\nSeu contrato para o aparelho {product['brand']} {product['model']} foi assinado com sucesso.\n\nContrato: {contract_url}"
            send_email(email, email_subject, email_body, pdf_path)
            
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
