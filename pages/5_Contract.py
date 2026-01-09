import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.pdf_service import generate_contract_pdf
from services.cep_service import get_address_from_cep
from services.email_service import send_email
import time
import datetime
import urllib.parse
import os

st.set_page_config(page_title="Trek - Detalhes e Contrato", page_icon="📝")

require_auth()

if "selected_product" not in st.session_state:
    st.warning("Nenhum aparelho selecionado. Volte para a loja.")
    if st.button("Ir para Loja"):
        st.switch_page("pages/3_Store.py")
    st.stop()

product = st.session_state["selected_product"]
user = st.session_state["user"]

# --- TELA 2: Detalhe do Aparelho / Aceite ---

st.title("Detalhes da Assinatura")

# Device Info
col_img, col_info = st.columns([1, 2])
with col_img:
    st.image(product.get("image_url", "https://via.placeholder.com/300"), use_container_width=True)

with col_info:
    st.header(f"{product['brand']} {product['model']}")
    st.write(product.get("description", ""))
    
    # CLOSED SCOPE: "Valor da assinatura com seguro (em destaque)"
    # We sum monthly + insurance for display as per request
    # Handle possible None values from DB using pricing service
    from services.pricing import calculate_contract_totals
    
    total_monthly, residual = calculate_contract_totals(product)
    
    st.metric(label="Valor Mensal com Seguro", value=f"R$ {total_monthly:.2f}")
    
    # Residual Value
    st.write(f"**Valor Residual:** R$ {residual}")
    
    c_vid_label, c_vid_btn = st.columns([1, 1])
    with c_vid_label:
        st.write("❓ O que é o Valor Residual?")
    
    # Video Logic
    # Assuming video is in root. Streamlit usually runs from root.
    video_path = "video residual.mp4"
    if os.path.exists(video_path):
        with open(video_path, 'rb') as v:
            video_bytes = v.read()
            st.video(video_bytes)
    else:
        st.warning("Vídeo explicativo não encontrado.")

st.divider()

# Mother Contract (Contrato-Mãe)
with st.expander("📄 Ler Contrato-Mãe (Termos Gerais)"):
    st.markdown("### Contrato de Locação de Equipamentos Móveis")
    st.write("Clique abaixo para baixar o contrato completo.")
    
    contract_path = "Contrato MÃE de assinatura de celular .docx"
    if os.path.exists(contract_path):
        with open(contract_path, "rb") as f:
            st.download_button(
                label="Baixar Contrato-Mãe (.docx)",
                data=f,
                file_name="Contrato_Mae_Celular.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.error("Arquivo de contrato não encontrado.")

# Acceptance
st.subheader("Aceite")
if "terms_accepted" not in st.session_state:
    st.session_state["terms_accepted"] = False

accepted = st.checkbox("Li e concordo com os termos do Contrato-Mãe e as condições acima.", value=st.session_state["terms_accepted"])

if accepted:
    st.session_state["terms_accepted"] = True
    # Log acceptance
    if "acceptance_log" not in st.session_state:
         st.session_state["acceptance_log"] = {
             "timestamp": datetime.datetime.now().isoformat(),
             "ip": "Simulated IP" 
         }

# --- TELA 3: Coleta de Dados (Só aparece se aceitou) ---

if st.session_state["terms_accepted"]:
    st.divider()
    st.header("Seus Dados")
    st.info("Preencha os dados restantes para gerar o Aditivo.")
    
    # Helper for CEP
    def search_cep():
        c = st.session_state.get("cep_input_temp", "")
        if c:
            res = get_address_from_cep(c)
            if res:
                st.session_state["addr_street"] = res.get("street", "")
                st.session_state["addr_neigh"] = res.get("neighborhood", "")
                st.session_state["addr_city"] = res.get("city", "")
                st.session_state["addr_state"] = res.get("state", "")
                st.toast("Endereço encontrado!", icon="✅")
            else:
                st.toast("CEP não encontrado.", icon="❌")

    # Form
    with st.form("contract_form"):
        # Name and CPF (Frozen from User Profile/Login)
        col_name, col_cpf = st.columns(2)
        with col_name:
            st.text_input("Nome", value=user.get("name", ""), disabled=True)
        with col_cpf:
            st.text_input("CPF", value=user.get("cpf", ""), disabled=True)
            
        st.markdown("#### Endereço")
        c_cep, c_btn = st.columns([3, 1])
        with c_cep:
            cep_val = st.text_input("CEP", key="cep_input_temp")
        with c_btn:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.form_submit_button("Buscar CEP", on_click=search_cep, type="secondary")

        # Auto-filled fields from session state if available
        acc_street = st.session_state.get("addr_street", "")
        acc_neigh = st.session_state.get("addr_neigh", "")
        
        col_str, col_num = st.columns([3, 1])
        with col_str:
            street_val = st.text_input("Rua/Logradouro", value=acc_street)
        with col_num:
            num_val = st.text_input("Número")
            
        col_comp, col_bairro = st.columns(2)
        with col_comp:
            comp_val = st.text_input("Complemento")
        with col_bairro:
            neigh_val = st.text_input("Bairro", value=acc_neigh)
            
        st.markdown("#### Contato")
        col_email, col_cell = st.columns(2)
        with col_email:
            email_val = st.text_input("E-mail", value=user.get("email", ""))
        with col_cell:
            cell_val = st.text_input("Celular (com DDD)", value=user.get("phone", ""))
            
        st.markdown("---")
        submitted = st.form_submit_button("Finalizar e Assinar", type="primary")
        
        if submitted:
            # required check: CEP, Number, Email, Mobile
            if not(cep_val and street_val and num_val and email_val and cell_val):
                st.error("Por favor, preencha CEP, Endereço, Número, Email e Celular.")
            else:
                with st.spinner("Gerando Aditivo..."):
                    # Construct full address string for PDF
                    # Format: Rua X, 123, Comp Y - Bairro Z - CEP 00000
                    full_address = f"{street_val}, {num_val}"
                    if comp_val:
                        full_address += f", {comp_val}"
                    full_address += f" - {neigh_val} - CEP {cep_val}"
                    
                    # Contract Data Packet
                    contract_data = {
                        "name": user["name"],
                        "cpf": user["cpf"],
                        "email": email_val,
                        "phone": cell_val,
                        "address": full_address,
                        "start_date": datetime.date.today().strftime("%d/%m/%Y"),
                        "end_date": (datetime.date.today() + datetime.timedelta(days=21*30)).strftime("%d/%m/%Y"), # Approx
                        "months": 21,
                        "value_monthly_total": total_monthly,
                        "residual_value": residual
                    }
                    
                    try:
                        # 1. Generate PDF
                        # We pass 'contract_data' which now matches exactly what the PDF Service should expect for the Closed Scope
                        # We need to make sure pdf_service uses these keys.
                        
                        pdf_path = generate_contract_pdf(contract_data, product, user.get("companies"))
                        
                        # 2. Save Order
                        supabase = get_supabase()
                        order_payload = {
                            "user_id": user["id"],
                            "product_id": product["id"],
                            "company_id": user["company_id"],
                            "status": "contract_signed",
                            "delivery_address": {
                                "full": full_address,
                                "cep": cep_val,
                                "street": street_val,
                                "number": num_val,
                                "complement": comp_val,
                                "neighborhood": neigh_val
                            },
                            "contract_url": pdf_path,
                            "signed_at": datetime.datetime.now().isoformat(),
                            "imei": None # Started empty
                        }
                        
                        supabase.table("orders").insert(order_payload).execute()
                        
                        # Update user contact info
                        try:
                            supabase.table("user_profiles").update({
                                "phone": cell_val, 
                                "email": email_val
                            }).eq("id", user["id"]).execute()
                        except:
                            pass
                        
                        st.success("Aditivo gerado e pedido realizado!")
                        st.toast("Pedido enviado para expedição.", icon="🚀")
                        
                        # WhatsApp Link (Optional/Nice to have from previous scope)
                        wa_text = f"Olá, assinei o aditivo do {product['brand']} {product['model']}! Aguardo expedição."
                        wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"
                        st.link_button("Avise no WhatsApp", wa_link)
                        
                        time.sleep(3)
                        st.switch_page("pages/1_Admin.py") # Redirect somewhere logic, or just stay
                        
                    except Exception as e:
                        st.error(f"Erro ao finalizar: {e}")
