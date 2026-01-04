import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.cep_service import get_address_from_cep

def test_get_address_from_cep_valid():
    # Known valid CEP (Sé Square in São Paulo)
    cep = "01001000"
    address = get_address_from_cep(cep)
    assert address is not None
    assert address["street"] == "Praça da Sé"
    assert address["city"] == "São Paulo"
    assert address["state"] == "SP"
    
def test_get_address_from_cep_invalid():
    # Invalid CEP
    cep = "00000000"
    address = get_address_from_cep(cep)
    assert address is None

def test_get_address_from_cep_format():
    # Valid CEP with punctuation
    cep = "01001-000"
    address = get_address_from_cep(cep)
    assert address is not None
    assert address["cep"] == "01001000"
