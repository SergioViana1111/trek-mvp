import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase

st.set_page_config(page_title="Trek - Loja", page_icon="🛍️")

require_auth()

st.title("Escolha seu Celular")

# Presentation Video
st.header("Conheça o Programa")
# Placeholder video
st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Replace with actual link

# Fetch company info
user = st.session_state.get("user")
if user and "companies" in user:
    company_name = user["companies"].get("name", "Sua Empresa")
    logo_url = user["companies"].get("logo_url")
    
    col_logo, col_name = st.columns([1, 4])
    with col_logo:
        if logo_url:
            st.image(logo_url, width=80)
    with col_name:
        st.subheader(company_name)

st.divider()

st.header("Aparelhos Disponíveis")

# Fetch products
supabase = get_supabase()
products = []
try:
    res = supabase.table("products").select("*").eq("active", True).execute()
    products = res.data
except:
    st.warning("Não foi possível carregar os produtos.")

# If no products in DB, show mock
if not products:
    products = [
        {
            "id": "mock1", 
            "brand": "Samsung", 
            "model": "Galaxy S23", 
            "monthly_price": 149.90, 
            "image_url": "https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_SX679_.jpg",
            "description": "128GB, Tela 6.1"
        },
        {
            "id": "mock2", 
            "brand": "Apple", 
            "model": "iPhone 14", 
            "monthly_price": 199.90, 
            "image_url": "https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_SX679_.jpg",
            "description": "128GB, Tela 6.1"
        }
    ]

# Display Grid
cols = st.columns(3)
for idx, prod in enumerate(products):
    col = cols[idx % 3]
    with col:
        st.image(prod.get("image_url") or "https://via.placeholder.com/150", use_container_width=True)
        st.subheader(f"{prod['brand']} {prod['model']}")
        st.write(prod.get("description", ""))
        st.write(f"**Mensalidade:** R$ {prod['monthly_price']}")
        
        if st.button("Escolher este", key=prod['id']):
            st.session_state["selected_product"] = prod
            st.switch_page("pages/5_Contract.py") # Or similar
