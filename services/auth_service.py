import streamlit as st
from services.supabase_client import get_supabase

def login_by_cpf(cpf: str, birth_date: str = None):
    """
    Simulates login by querying the user_profiles table for a matching CPF and Birth Date.
    """
    supabase = get_supabase()
    if not supabase:
        return False, "Database connection error."

    # Normalize CPF (strip non-digits)
    clean_cpf = "".join(filter(str.isdigit, cpf))
    
    try:
        # Query user
        query = supabase.table("user_profiles").select("*, companies(name, logo_url)").eq("cpf", clean_cpf)
        
        # If birth_date provided, check it (assuming format YYYY-MM-DD or similar in DB)
        # Note: In real production, handle date formats carefully.
        # For this MVP, we compare string if passed.
        if birth_date:
             query = query.eq("birth_date", str(birth_date))
        
        data = query.execute()
        
        if data.data and len(data.data) > 0:
            user = data.data[0]
            if not user.get("active"):
                return False, "User is inactive."
            
            # Set session state
            st.session_state["user"] = user
            st.session_state["logged_in"] = True
            st.session_state["role"] = user.get("role", "employee")
            return True, "Login successful."
        else:
            return False, "CPF not found."
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def logout():
    st.session_state.clear()
    st.rerun()

def get_current_user():
    return st.session_state.get("user")

def require_auth():
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to continue.")
        st.stop()
