import sys
import os
import toml
import pytest
from supabase import create_client
import datetime
from dateutil.relativedelta import relativedelta
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.auth_service import login_by_cpf
from services.pdf_service import generate_contract_pdf

SECRETS_PATH = os.path.join(os.path.dirname(__file__), '..', 'secrets.toml')

@pytest.fixture
def supabase():
    if not os.path.exists(SECRETS_PATH):
        pytest.skip("Supabase credentials not found.")
    secrets = toml.load(SECRETS_PATH)
    url = secrets["supabase"]["url"]
    key = secrets["supabase"]["key"]
    return create_client(url, key)

@pytest.fixture
def test_data(supabase):
    # Create unique test entities to avoid conflicts
    unique_id = int(time.time())
    
    # 1. Company
    company_data = {
        "cnpj": f"00.000.000/0002-{unique_id % 1000}", # Mock CNPJ
        "name": f"Test Company {unique_id}",
        "address": "Test Address"
    }
    res_comp = supabase.table("companies").insert(company_data).execute()
    company = res_comp.data[0]
    
    # 2. User
    user_data = {
        "company_id": company["id"],
        "name": "Integration Tester",
        "cpf": f"111222333{unique_id % 100}", # Mock CPF
        "birth_date": "1990-01-01",
        "role": "employee",
        "active": True
    }
    res_user = supabase.table("user_profiles").insert(user_data).execute()
    user = res_user.data[0]
    
    # 3. Product
    prod_data = {
        "brand": "TestBrand",
        "model": f"TestModel {unique_id}",
        "description": "Test Desc",
        "monthly_price": 50.00,
        "insurance_price": 10.0,
        "residual_value": 200.0,
        "active": True
    }
    res_prod = supabase.table("products").insert(prod_data).execute()
    product = res_prod.data[0]
    
    yield {
        "company": company,
        "user": user,
        "product": product
    }
    
    # Cleanup (Optional)
    # supabase.table("orders").delete().eq("user_id", user["id"]).execute()
    # supabase.table("user_profiles").delete().eq("id", user["id"]).execute()
    # supabase.table("products").delete().eq("id", product["id"]).execute()
    # supabase.table("companies").delete().eq("id", company["id"]).execute()

def test_full_purchase_flow(supabase, test_data):
    """
    Tests the complete happy path:
    Login -> View Product -> Generate Contract -> Create Order -> Admin Dispatch
    """
    user = test_data["user"]
    product = test_data["product"]
    company = test_data["company"]
    
    print(f"\n[TEST] Starting flow for User {user['cpf']} and Product {product['model']}")

    # 1. Test Login Service
    print("[1] Testing Login...")
    success, msg = login_by_cpf(user["cpf"], "1990-01-01")
    assert success, f"Login failed: {msg}"
    
    # 2. Simulate User Acceptance & PDF Generation
    print("[2] Generating Contract PDF...")
    
    total_monthly = float(product["monthly_price"]) + float(product["insurance_price"])
    start_date = datetime.date.today()
    end_date = start_date + relativedelta(months=21)
    
    contract_info = {
        "name": user["name"],
        "cpf": user["cpf"],
        "email": "test@example.com",
        "phone": "11999999999",
        "address": "Rua Teste, 123 - Bairro - CEP 00000000",
        "start_date": start_date.strftime("%d/%m/%Y"),
        "end_date": end_date.strftime("%d/%m/%Y"),
        "months": 21,
        "value_monthly_total": total_monthly,
        "residual_value": product["residual_value"],
        "acceptance_date": datetime.datetime.now().isoformat()
    }
    
    pdf_path = generate_contract_pdf(contract_info, product, company)
    assert os.path.exists(pdf_path), "PDF was not generated"
    print(f"    PDF generated at: {pdf_path}")
    
    # 3. Create Order (Simulate 'Contract' page submit)
    print("[3] Creating Order...")
    order_payload = {
        "user_id": user["id"],
        "product_id": product["id"],
        "company_id": company["id"],
        "status": "contract_signed",
        "contract_url": pdf_path,
        "signed_at": datetime.datetime.now().isoformat(),
        "delivery_address": {
            "full": contract_info["address"],
            "cep": "00000-000"
        }
    }
    res_order = supabase.table("orders").insert(order_payload).execute()
    assert res_order.data, "Order creation failed"
    order = res_order.data[0]
    assert order["status"] == "contract_signed"
    print(f"    Order {order['id']} created.")
    
    # 4. Admin Dispatch (Simulate Admin page action)
    print("[4] Admin Dispatching Order...")
    imei = "123456789012345"
    
    # Update order to dispatched
    res_update = supabase.table("orders").update({
        "status": "dispatched",
        "imei": imei
    }).eq("id", order["id"]).execute()
    
    updated_order = res_update.data[0]
    assert updated_order["status"] == "dispatched"
    assert updated_order["imei"] == imei
    print(f"    Order dispatched with IMEI {imei}.")
    
    # 5. Regenerate Contract with IMEI
    print("[5] Regenerating Contract with IMEI...")
    prod_with_imei = product.copy()
    prod_with_imei["imei"] = imei
    
    pdf_path_final = generate_contract_pdf(contract_info, prod_with_imei, company)
    assert os.path.exists(pdf_path_final)
    
    print(f"    Final PDF generated: {pdf_path_final}")
    
    print("[SUCCESS] Full flow integration test passed.")

    # Clean up PDF files
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(pdf_path_final):
            os.remove(pdf_path_final)
    except:
        pass
