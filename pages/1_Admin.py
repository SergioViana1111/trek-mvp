import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.consult_service import consult_cnpj, consult_cpf
import datetime

# Page config
st.set_page_config(page_title="Trek - Admin", page_icon="🔒")

# Check Auth
require_auth()

if st.session_state.get("role") != "admin":
    st.error("Acesso negado. Apenas administradores podem ver esta página.")
    st.stop()

st.title("Painel Admin (IBUG)")

tab1, tab2 = st.tabs(["Minhas Empresas", "Pedidos"])

# Function to search CNPJ
def handle_cnpj_search():
    cnpj_input = st.session_state.get("cnpj_input", "")
    if cnpj_input:
        with st.spinner("Buscando CNPJ..."):
            data = consult_cnpj(cnpj_input)
            if data:
                st.session_state["name_input"] = data.get("name", "")
                st.session_state["address_input"] = data.get("address", "")
                st.toast("CNPJ encontrado!", icon="✅")
            else:
                st.toast("CNPJ não encontrado ou erro na busca.", icon="❌")

# Function to search CPF
def handle_cpf_search():
    cpf_input = st.session_state.get("resp_cpf_input", "")
    if cpf_input:
        with st.spinner("Buscando CPF..."):
            data = consult_cpf(cpf_input)
            if data:
                st.session_state["resp_name_input"] = data.get("name", "")
                st.session_state["resp_dob_input"] = data.get("birth_date")
                st.toast("CPF encontrado!", icon="✅")
            else:
                st.toast("CPF não encontrado.", icon="❌")

with tab1:
    st.header("Gestão de Empresas")
    
    # Form to add company
    with st.expander("Nova Empresa", expanded=True):
        st.markdown("##### Dados da Empresa")
        col_cnpj, col_btn_cnpj = st.columns([3, 1])
        with col_cnpj:
            cnpj = st.text_input("CNPJ", key="cnpj_input")
        with col_btn_cnpj:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Buscar CNPJ"):
                handle_cnpj_search()
                st.rerun()
                
        name = st.text_input("Razão Social", key="name_input")
        address = st.text_area("Endereço", key="address_input")
        logo_url = st.text_input("URL Logo")
        
        st.markdown("---")
        st.markdown("##### Dados do Responsável")
        
        col_cpf, col_btn_cpf = st.columns([3, 1])
        with col_cpf:
            resp_cpf = st.text_input("CPF Responsável", key="resp_cpf_input")
        with col_btn_cpf:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Buscar CPF"):
                handle_cpf_search()
                st.rerun()

        col_name, col_dob = st.columns([2, 1])
        with col_name:
            resp_name = st.text_input("Nome Responsável", key="resp_name_input")
        with col_dob:
            resp_dob = st.date_input("Data de Nascimento", value=None, key="resp_dob_input")

        col_email, col_phone = st.columns(2)
        with col_email:
            resp_email = st.text_input("E-mail Responsável")
        with col_phone:
            resp_phone = st.text_input("Celular Responsável")
            
        submitted = st.button("Cadastrar Empresa")
        if submitted:
            if not (name and cnpj and resp_cpf and resp_name):
                 st.error("Preencha os campos obrigatórios.")
            else:
                supabase = get_supabase()
                try:
                    data = {
                        "name": name,
                        "cnpj": cnpj,
                        "address": address,
                        "logo_url": logo_url,
                        "responsible_cpf": resp_cpf,
                        "responsible_name": resp_name,
                        "responsible_email": resp_email,
                        "responsible_phone": resp_phone,
                        "responsible_birth_date": str(resp_dob) if resp_dob else None
                    }
                    supabase.table("companies").insert(data).execute()
                    st.success("Empresa cadastrada com sucesso!")
                    # Clear form (optional)
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")

    # List companies
    try:
        supabase = get_supabase()
        res = supabase.table("companies").select("*").execute()
        if res.data:
            st.markdown("### Empresas Cadastradas")
            for comp in res.data:
                with st.container():
                    st.markdown(f"**{comp['name']}**")
                    st.caption(f"CNPJ: {comp['cnpj']} | Resp: {comp.get('responsible_name', 'N/A')}")
                    st.markdown("---")
    except Exception as e:
        st.error(f"Erro ao carregar empresas: {e}")

with tab2:
    st.header("Todos os Pedidos")
    st.info("Funcionalidade de listagem de pedidos em breve...")

