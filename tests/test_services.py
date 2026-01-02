import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path so we can import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.supabase_client import SupabaseService, get_supabase
from services.auth_service import login_by_cpf, require_auth, logout
from services.pdf_service import generate_contract_pdf

# Mock Streamlit secrets and session state
@pytest.fixture(autouse=True)
def mock_streamlit():
    with patch('services.supabase_client.st') as mock_st:
        mock_st.secrets = {"supabase": {"url": "https://mock.supabase.co", "key": "mock_key"}}
        yield mock_st

@pytest.fixture
def mock_supabase():
    with patch('services.supabase_client.create_client') as mock_create:
        client_instance = MagicMock()
        mock_create.return_value = client_instance
        # Reset singleton logic for tests
        SupabaseService._instance = None 
        yield client_instance

def test_supabase_singleton(mock_supabase):
    """Test that SupabaseService returns a singleton client."""
    client1 = get_supabase()
    client2 = get_supabase()
    assert client1 is client2
    assert client1 is mock_supabase

from services.email_service import send_email

# ... (Previous fixtures remain)

def test_login_success(mock_supabase):
    """Test successful login with valid CPF and DOB."""
    # Mock DB response
    mock_user = {"id": "123", "name": "Test User", "role": "employee", "active": True}
    mock_response = MagicMock()
    mock_response.data = [mock_user]
    
    # Chain: table().select().eq().eq().execute()
    # We need to simulate the chaining of .eq() since we added birth_date check
    mock_query = MagicMock()
    mock_query.execute.return_value = mock_response
    mock_query.eq.return_value = mock_query # Allow chaining
    
    mock_supabase.table.return_value.select.return_value.eq.return_value = mock_query 

    with patch('services.auth_service.st') as mock_st:
        mock_st.session_state = {}
        # Test valid login
        success, msg = login_by_cpf("123.456.789-00", "1990-01-01")
        
        assert success is True
        assert mock_st.session_state["logged_in"] is True
        assert mock_st.session_state["user"] == mock_user

def test_login_invalid_cpf(mock_supabase):
    mock_response = MagicMock()
    mock_response.data = []
    mock_query = MagicMock()
    mock_query.execute.return_value = mock_response
    mock_query.eq.return_value = mock_query
    
    mock_supabase.table.return_value.select.return_value.eq.return_value = mock_query
    
    with patch('services.auth_service.st') as mock_st:
        mock_st.session_state = {}
        success, msg = login_by_cpf("000", "1990-01-01")
        assert success is False

def test_email_service_mock():
    """Test that email service 'sends' (returns True) when mocked."""
    with patch('services.email_service.st') as mock_st:
        # Simulate no secrets => mock mode
        mock_st.secrets = {}
        result = send_email("test@test.com", "Subject", "Body")
        assert result is True


def test_pdf_generation():
    """Test PDF generation creates a file."""
    user = {"name": "Test User", "cpf": "123"}
    product = {"brand": "TestBrand", "model": "TestModel", "monthly_price": 100}
    company = {"name": "TestCompany", "cnpj": "000"}
    
    try:
        path = generate_contract_pdf(user, product, company)
        assert os.path.exists(path)
        assert path.endswith(".pdf")
    finally:
        # Cleanup
        if os.path.exists(path):
            os.remove(path)
