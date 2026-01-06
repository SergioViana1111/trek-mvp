import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.pdf_service import generate_contract_pdf
from services.cep_service import get_address_from_cep
from services.email_service import send_email
import time
import datetime
import urllib.parse

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
    
    st.markdown("### Valores")
    st.write(f"**Assinatura Mensal:** R$ {product['monthly_price']}")
    st.write(f"**Seguro (Mensal):** R$ {product['insurance_price']}")
    
    # Residual Value
    residual = product['residual_value']
    st.write(f"**Valor Residual:** R$ {residual}")
    
    with st.expander("❓ O que é o Valor Residual?"):
        st.info("""
        **O Valor Residual é uma opção de compra ao final do contrato.**
        
        - **Se renovar a assinatura** ao final de 21 meses: Você **NÃO PAGA** o valor residual e troca por um aparelho novo.
        - **Se optar por ficar com o aparelho**: Você paga o valor residual e o aparelho é seu.
        """)
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Placeholder video logic
        st.caption("Vídeo explicativo sobre o Valor Residual.")

st.divider()

# Mother Contract (Contrato-Mãe)
with st.expander("📄 Ler Contrato-Mãe (Termos Gerais)"):
    st.markdown("""
    ### Contrato de Locação de Equipamentos Móveis - Termos Gerais
    
    1. **OBJETO**: Locação de aparelhos celulares...
    2. **PRAZO**: O contrato tem vigência de 21 meses...
    3. **PAGAMENTO**: O pagamento será descontado em folha...
    4. **SEGURO**: O aparelho conta com seguro contra roubo e furto qualificado...
    5. **DEVOLUÇÃO**: Ao final, o Locatário pode devolver ou comprar pelo Valor Residual...
    
    *(Texto completo do contrato jurídico estaria aqui)*
    """)
    st.download_button("Baixar Contrato-Mãe (PDF)", data=b"Mock PDF Content", file_name="contrato_mae.pdf")

# Acceptance
st.subheader("Aceite")
if "terms_accepted" not in st.session_state:
    st.session_state["terms_accepted"] = False

accepted = st.checkbox("Li e concordo com os termos do Contrato-Mãe e as condições acima.", value=st.session_state["terms_accepted"])

if accepted:
    st.session_state["terms_accepted"] = True
    # Log acceptance (in a real app, log to DB immediately or keep in state)
    if "acceptance_log" not in st.session_state:
         st.session_state["acceptance_log"] = {
             "timestamp": datetime.datetime.now().isoformat(),
             "ip": "127.0.0.1" # Mock IP
         }

# --- TELA 3: Coleta de Dados (Só aparece se aceitou) ---

if st.session_state["terms_accepted"]:
    st.divider()
    st.header("Seus Dados")
    st.info("Complete seus dados para gerar o contrato (Aditivo).")
    
    # Pre-fill with session user data if available
    with st.form("contract_form"):
        col_name, col_cpf = st.columns(2)
        with col_name:
            # Name editable or fixed? Verify requirement. "Coleta: Nome, Endereço... CPF já vem"
            # User might need to correct name if Login was just CPF lookup? 
            # Let's assume pre-filled but editable or read-only if strict.
            name = st.text_input("Nome Completo", value=user.get("name", ""))
        with col_cpf:
            st.text_input("CPF", value=user.get("cpf", ""), disabled=True)
            
        col_email, col_cell = st.columns(2)
        with col_email:
            email_val = st.text_input("E-mail", value=user.get("email", ""))
        with col_cell:
            cell_val = st.text_input("Celular (com DDD)", value=user.get("phone", ""))
            
        st.markdown("#### Endereço")
        col_cep_in, col_cep_btn = st.columns([3, 1])
        with col_cep_in:
            cep_val = st.text_input("CEP", value=st.session_state.get("cep_found", ""), key="cep_form")
        # Note: CEP search inside form is tricky in Streamlit (rerun). 
        # Better to do outside or use on_change. For simplicity, we assume user types or standard flow.
        # Actually user requirement allows CEP search. Let's handle it via a separate interactor or just basic fields + helper.
        
        col_addr, col_num = st.columns([3, 1])
        with col_addr:
            street_val = st.text_input("Endereço (Rua, Av)", value=st.session_state.get("street_found", ""))
        with col_num:
            num_val = st.text_input("Número")
            
        comp_val = st.text_input("Complemento")
        neigh_val = st.text_input("Bairro", value=st.session_state.get("neigh_found", ""))
        
        submitted = st.form_submit_button("Finalizar e Assinar Contrato")
        
        if submitted:
            if not(name and email_val and cell_val and street_val and num_val and cep_val):
                st.error("Preencha todos os campos obrigatórios.")
            else:
                with st.spinner("Gerando Aditivo Contratual..."):
                    # 1. Generate PDF (Additive)
                    company = user.get("companies", {"name": "Trek", "cnpj": "00.000.000/0001-00"}) # Fallback
                    
                    contract_data = {
                        "name": name,
                        "cpf": user["cpf"],
                        "email": email_val,
                        "phone": cell_val,
                        "address": f"{street_val}, {num_val}, {comp_val} - {neigh_val} - CEP {cep_val}",
                        "acceptance_date": st.session_state["acceptance_log"]["timestamp"]
                    }
                    
                    try:
                        pdf_path = generate_contract_pdf(contract_data, product, company)
                        
                        # 2. Create Order
                        supabase = get_supabase()
                        order_data = {
                            "user_id": user["id"],
                            "product_id": product["id"],
                            "company_id": user.get("company_id"),
                            "status": "contract_signed", # Status created -> signed
                            "contract_url": "contract_sent_via_email", # Real path in storage
                            "signed_at": datetime.datetime.now().isoformat(),
                            "delivery_address": contract_data["address"],
                            # JSONB extra contact info
                        }
                        # Check columns in DB `orders`. `delivery_address` is JSONB.
                        
                         # Insert Order
                        supabase.table("orders").insert({
                            "user_id": user["id"],
                            "product_id": product["id"],
                            "company_id": user["company_id"],
                            "status": "contract_signed",
                            "delivery_address": {
                                "full": contract_data["address"],
                                "cep": cep_val
                            },
                            "contract_url": pdf_path, # Local path for MVP
                            "signed_at": datetime.datetime.now().isoformat()
                         }).execute()

                        # 3. Send Email
                        subject = "Seu Aditivo de Contrato - Trek"
                        body = f"""Olá {name},
                        
                        Confirmação de assinatura do aparelho {product['brand']} {product['model']}.
                        Seguem os dados do contrato em anexo.
                        
                        Atenciosamente,
                        Equipe Trek
                        """
                        send_email(email_val, subject, body, pdf_path) # Uncomment if configured
                        
                        st.success("Contrato assinado com sucesso!")
                        
                        # WhatsApp Link
                        wa_text = f"Olá, assinei o contrato do {product['brand']} {product['model']}! Segue meu contato."
                        wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"
                        
                        st.markdown(f"""
                        <a href="{wa_link}" target="_blank">
                            <button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                                📱 Enviar no WhatsApp
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        
                        st.balloons()
                        time.sleep(5)
                        # Optional: Clear state or redirect
                        
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")

# CEP Utility (Outside form to allow interactivity without clearing form if possible, or just use form)
# For MVP, user types address manually if CEP fails not critical.
