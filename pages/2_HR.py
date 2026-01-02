import streamlit as st
import pandas as pd
from services.auth_service import require_auth
from services.supabase_client import get_supabase

st.set_page_config(page_title="Trek - RH", page_icon="👥")

require_auth()
if st.session_state.get("role") not in ["admin", "hr"]:
    st.error("Acesso negado.")
    st.stop()

st.title("Portal do RH")

tab1, tab2 = st.tabs(["Gestão de Funcionários", "Relatórios"])

with tab1:
    st.header("Importar Funcionários")
    st.markdown("Faça upload de um arquivo CSV ou Excel com as colunas: `Nome`, `CPF`, `Email`.")
    
    uploaded_file = st.file_uploader("Arquivo de Funcionários", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head())
            
            if st.button("Processar Upload"):
                # Mock processing logic
                st.info("Processando...")
                # Iterate and upsert to Supabase
                # supabase = get_supabase()
                # for index, row in df.iterrows():
                #    ... upsert user_profiles ...
                st.success("Funcionários importados com sucesso! (Simulação)")
                
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

with tab2:
    st.header("Relatórios Financeiros")
    st.write("Baixar arquivo de descontos em folha.")
    if st.button("Gerar Relatório de Descontos"):
        st.success("Relatório gerado! (Simulação de Download)")
