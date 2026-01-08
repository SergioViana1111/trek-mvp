import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase
from services.consult_service import consult_cnpj, consult_cpf
from services.pdf_service import generate_contract_pdf
import datetime
from dateutil.relativedelta import relativedelta

# Page config
st.set_page_config(page_title="Trek - Admin", page_icon="🔒")

# Check Auth
require_auth()

if st.session_state.get("role") != "admin":
    st.error("Acesso negado. Apenas administradores podem ver esta página.")
    st.stop()

st.title("Painel Admin (IBUG)")

tab1, tab2, tab3 = st.tabs(["Minhas Empresas", "Produtos (Celulares)", "Pedidos (Expedição)"])

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
    with st.expander("Nova Empresa", expanded=False):
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
    st.header("Gestão de Produtos (Celulares)")
    
    # Form to add product
    with st.expander("Novo Celular"):
        with st.form("new_product"):
            p_brand = st.text_input("Marca (ex: Samsung)")
            p_model = st.text_input("Modelo (ex: Galaxy S23)")
            p_img = st.text_input("URL da Imagem")
            p_desc = st.text_area("Descrição do Aparelho")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                p_price = st.number_input("Valor Mensal (R$)", min_value=0.0, step=10.0)
            with c2:
                p_insur = st.number_input("Seguro (R$)", min_value=0.0, step=10.0)
            with c3:
                p_resid = st.number_input("Valor Residual (R$)", min_value=0.0, step=10.0)
            
            p_submit = st.form_submit_button("Cadastrar Celular")
            if p_submit:
                if not (p_brand and p_model and p_price):
                    st.error("Preencha Marca, Modelo e Valor.")
                else:
                    supabase = get_supabase()
                    try:
                        p_data = {
                            "brand": p_brand,
                            "model": p_model,
                            "description": p_desc,
                            "image_url": p_img,
                            "monthly_price": p_price,
                            "insurance_price": p_insur,
                            "residual_value": p_resid,
                            "active": True
                        }
                        supabase.table("products").insert(p_data).execute()
                        st.success(f"📱 {p_brand} {p_model} cadastrado!")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")

    # List products
    try:
        supabase = get_supabase()
        res_prod = supabase.table("products").select("*").order("created_at", desc=True).execute()
        
        if res_prod.data:
            st.markdown("### Catálogo Atual")
            for prod in res_prod.data:
                with st.container():
                    c_img, c_info, c_actions = st.columns([1, 3, 1])
                    with c_img:
                        if prod.get("image_url"):
                            st.image(prod["image_url"], width=80)
                        else:
                            st.write("🖼️")
                    
                    with c_info:
                        st.subheader(f"{prod['brand']} {prod['model']}")
                        st.write(f"Mensal: R$ {prod['monthly_price']} | Ativo: {'✅' if prod['active'] else '❌'}")
                        
                    with c_actions:
                        # Simple toggle active
                        if st.button(f"{'Desativar' if prod['active'] else 'Ativar'}", key=f"toggle_{prod['id']}"):
                            new_status = not prod['active']
                            supabase.table("products").update({"active": new_status}).eq("id", prod['id']).execute()
                            st.rerun()
                        
                    st.divider()
                    
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")


with tab3:
    st.header("Fila de Pedidos")
    
    try:
        supabase = get_supabase()
        # Join query
        res_orders = supabase.table("orders").select(
            "*, user_profiles(name, cpf, email, phone), products(*)"
        ).order("created_at", desc=True).execute()
        
        orders = res_orders.data
        if not orders:
            st.info("Nenhum pedido encontrado.")
        else:
            for order in orders:
                user_info = order.get("user_profiles", {}) or {}
                prod_info = order.get("products", {}) or {}
                status = order.get("status")
                
                with st.container():
                    st.markdown(f"**Pedido #{str(order['id'])[:8]}** - Status: `{status.upper()}`")
                    col_det, col_act = st.columns([2, 1])
                    
                    with col_det:
                        st.write(f"👤 **{user_info.get('name', 'N/A')}** ({user_info.get('cpf', 'N/A')})")
                        st.write(f"📱 {prod_info.get('brand')} {prod_info.get('model')}")
                        st.caption(f"Data: {order.get('created_at')}")
                        if status == 'dispatched':
                             st.success(f"IMEI vinculado: {order.get('imei')}")
                    
                    with col_act:
                        if status == "contract_signed":
                            imei_input = st.text_input(f"IMEI", key=f"imei_{order['id']}")
                            if st.button("Expedir", key=f"btn_{order['id']}"):
                                if imei_input:
                                    # Update Order
                                    supabase.table("orders").update({
                                        "status": "dispatched",
                                        "imei": imei_input
                                    }).eq("id", order['id']).execute()
                                    
                                    # Regenerate PDF with IMEI
                                    # Calculate dates
                                    signed_at_dt = datetime.datetime.fromisoformat(order['signed_at'])
                                    start_date = signed_at_dt.strftime("%d/%m/%Y")
                                    end_date_dt = signed_at_dt + relativedelta(months=21)
                                    end_date = end_date_dt.strftime("%d/%m/%Y")
                                    
                                    # Address
                                    deliv = order.get('delivery_address', {})
                                    address_str = ""
                                    if isinstance(deliv, dict):
                                        address_str = deliv.get('full', "")
                                    else:
                                        address_str = str(deliv)
                                    
                                    total_monthly = float(prod_info.get('monthly_price', 0)) + float(prod_info.get('insurance_price', 0))
                                    
                                    contract_data = {
                                        "name": user_info.get("name"),
                                        "cpf": user_info.get("cpf"),
                                        "email": user_info.get("email"),
                                        "phone": user_info.get("phone"),
                                        "address": address_str,
                                        "start_date": start_date,
                                        "end_date": end_date,
                                        "months": 21,
                                        "value_monthly_total": total_monthly,
                                        "residual_value": prod_info.get('residual_value'),
                                        "acceptance_date": order.get("signed_at")
                                    }
                                    
                                    # Inject IMEI into product data copy
                                    prod_with_imei = prod_info.copy()
                                    prod_with_imei["imei"] = imei_input
                                    
                                    # Company fetch (generic)
                                    company_res = supabase.table("companies").select("*").eq("id", order["company_id"]).execute()
                                    company_data = company_res.data[0] if company_res.data else {}
                                    
                                    new_pdf = generate_contract_pdf(contract_data, prod_with_imei, company_data)
                                    
                                    st.success(f"Pedido expedido! PDF atualizado: {new_pdf}")
                                    st.rerun()
                                else:
                                    st.error("Informe o IMEI.")
                        elif status == "dispatched":
                            st.write("✅ Concluído")
                            
                    st.divider()
                    
    except Exception as e:
        st.error(f"Erro ao carregar pedidos: {e}")
