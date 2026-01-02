import streamlit as st
from services.auth_service import require_auth
from services.supabase_client import get_supabase

st.set_page_config(page_title="Trek - Expedição", page_icon="📦")

require_auth()
if st.session_state.get("role") not in ["admin", "dispatch"]:
    st.error("Acesso negado.")
    st.stop()

st.title("Expedição de Pedidos")

supabase = get_supabase()

# Fetch orders ready for dispatch
# Status: contract_signed (waiting for IMEI) or imei_linked (waiting for dispatch)
try:
    res = supabase.table("orders").select("*, products(brand, model), user_profiles(name, cpf)").in_("status", ["contract_signed", "imei_linked"]).execute()
    orders = res.data
except:
    orders = []

if not orders:
    st.info("Nenhum pedido pendente de expedição.")
else:
    for order in orders:
        with st.expander(f"Pedido #{str(order['id'])[:8]} - {order['user_profiles']['name']}"):
            st.write(f"**Aparelho:** {order['products']['brand']} {order['products']['model']}")
            st.write(f"**Status:** {order['status']}")
            
            # Action: Link IMEI
            if order['status'] == 'contract_signed':
                new_imei = st.text_input("Inserir IMEI", key=f"imei_{order['id']}")
                if st.button("Vincular IMEI", key=f"btn_imei_{order['id']}"):
                    # Update order
                    supabase.table("orders").update({"imei": new_imei, "status": "imei_linked"}).eq("id", order['id']).execute()
                    
                    # Notify User via Email (Mock)
                    from services.email_service import send_email
                    user_email = order['user_profiles'].get('email')
                    send_email(user_email, "Trek - Aparelho Preparado", f"Seu aparelho foi vinculado ao IMEI: {new_imei}. Em breve será expedido.")

                    st.success("IMEI vinculado!")
                    st.rerun()

            # Action: Dispatch
            elif order['status'] == 'imei_linked':
                st.write(f"**IMEI:** {order['imei']}")
                if st.button("Marcar como Expedido", key=f"btn_disp_{order['id']}"):
                    # Update order
                    supabase.table("orders").update({"status": "dispatched"}).eq("id", order['id']).execute()
                    
                    # Notify User
                    from services.email_service import send_email
                    user_email = order['user_profiles'].get('email')
                    send_email(user_email, "Trek - Aparelho Expedido", f"Seu aparelho foi expedido! Aguarde a entrega.")
                    
                    # WhatsApp Link for Dispatcher to notify manually if needed
                    import urllib.parse
                    msg_text = f"Olá {order['user_profiles']['name']}, seu aparelho (IMEI {order['imei']}) saiu para entrega!"
                    encoded_text = urllib.parse.quote(msg_text)
                    wa_link = f"https://wa.me/?text={encoded_text}"
                    st.markdown(f"[📲 Abrir WhatsApp para avisar funcionário]({wa_link})")

                    st.success("Pedido expedido!")
                    time.sleep(3)
                    st.rerun()
