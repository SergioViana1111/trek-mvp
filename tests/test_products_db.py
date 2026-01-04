import sys
import os
import toml
import pytest
from supabase import create_client
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SECRETS_PATH = os.path.join(os.path.dirname(__file__), '..', '.streamlit', 'secrets.toml')

def get_test_supabase_client():
    if not os.path.exists(SECRETS_PATH):
        return None
    
    try:
        secrets = toml.load(SECRETS_PATH)
        url = secrets["supabase"]["url"]
        key = secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        print(f"Error loading secrets: {e}")
        return None

def test_create_and_fetch_product():
    supabase = get_test_supabase_client()
    if not supabase:
        pytest.skip("Supabase credentials not found or invalid.")
    
    # Random suffix to avoid clutter
    suffix = str(int(time.time()))
    brand = f"TestBrand_{suffix}"
    model = f"TestModel_{suffix}"
    
    # 1. Create
    data = {
        "brand": brand,
        "model": model,
        "description": "Test Description",
        "monthly_price": 99.90,
        "active": True
    }
    
    try:
        res = supabase.table("products").insert(data).execute()
        assert res.data, "Failed to insert product"
        product_id = res.data[0]["id"]
        
        # 2. Fetch
        res_fetch = supabase.table("products").select("*").eq("id", product_id).execute()
        assert res_fetch.data
        assert res_fetch.data[0]["brand"] == brand
        
        # 3. Update (Deactivate)
        res_update = supabase.table("products").update({"active": False}).eq("id", product_id).execute()
        assert res_update.data
        assert res_update.data[0]["active"] == False
        
        # Cleanup (Optional, but good practice if RLS allows delete)
        # supabase.table("products").delete().eq("id", product_id).execute()
        
    except Exception as e:
        pytest.fail(f"Supabase interaction failed: {e}")
