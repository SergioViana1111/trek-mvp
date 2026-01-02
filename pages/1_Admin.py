import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase

# Page config
st.set_page_config(page_title="Trek - Admin", page_icon="🔒")

# Check Auth
require_auth()

if st.session_state.get("role") != "admin":
    st.error("Acesso negado. Apenas administradores podem ver esta página.")
    st.stop()

st.title("Painel Admin (IBUG)")

tab1, tab2 = st.tabs(["Minhas Empresas", "Pedidos"])

with tab1:
    st.header("Gestão de Empresas")
    
    # Form to add company
    with st.expander("Nova Empresa"):
        with st.form("new_company"):
            name = st.text_input("Razão Social")
            cnpj = st.text_input("CNPJ")
            resp_cpf = st.text_input("CPF Responsável")
            address = st.text_area("Endereço")
            logo_url = st.text_input("URL Logo")
            
            submitted = st.form_submit_button("Cadastrar")
            if submitted:
                supabase = get_supabase()
                try:
                    data = {
                        "name": name,
                        "cnpj": cnpj,
                        "responsible_cpf": resp_cpf,
                        "address": address,
                        "logo_url": logo_url
                    }
                    supabase.table("companies").insert(data).execute()
                    st.success("Empresa cadastrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")

    # List companies
    try:
        supabase = get_supabase()
        res = supabase.table("companies").select("*").execute()
        if res.data:
            for comp in res.data:
                st.write(f"🏢 **{comp['name']}** - {comp['cnpj']}")
    except Exception as e:
        st.error(f"Erro ao carregar empresas: {e}")

with tab2:
    st.header("Todos os Pedidos")
    st.info("Funcionalidade de listagem de pedidos em breve...")
