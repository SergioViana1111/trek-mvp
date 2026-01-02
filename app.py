import streamlit as st
from services.auth_service import login_by_cpf, logout

st.set_page_config(page_title="Trek - Celular por Assinatura", page_icon="📱", layout="centered")

# Hide default sidebar functionality if user is not logged in can be tricky,
# but we can just use conditional rendering for the main content.
# Streamlit will still show the sidebar nav if pages exist.

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def main():
    if st.session_state["logged_in"]:
        user = st.session_state["user"]
        st.sidebar.title(f"Olá, {user['name']}")
        st.sidebar.text(user.get("role", "Employee").upper())
        if st.sidebar.button("Sair"):
            logout()
        
        st.title("Bem-vindo à Trek")
        st.write("Selecione uma opção no menu lateral para continuar.")
        
        # Simple dashboard summary could go here
        return

    # Login Screen
    st.title("📱 Trek")
    st.subheader("Login")
    
    cpf_input = st.text_input("Digite seu CPF", max_chars=14)
    # Using text_input for date to avoid date format confusion in MVP quick auth, 
    # or use date_input and format it. Let's use date_input.
    dob_input = st.date_input("Data de Nascimento", value=None, min_value=None, max_value=None, format="DD/MM/YYYY")
    
    if st.button("Entrar"):
        if cpf_input and dob_input:
            # Convert date to string YYYY-MM-DD to match Supabase Date type usually
            dob_str = dob_input.strftime("%Y-%m-%d")
            success, msg = login_by_cpf(cpf_input, dob_str)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        else:
            st.warning("Por favor, preencha CPF e Data de Nascimento.")

if __name__ == "__main__":
    main()
