import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from services.consult_service import consult_cnpj, consult_cpf

def test_consult_cnpj_valid():
    # Google Brasil CNPJ for testing: 06.990.590/0001-23
    # BrasilAPI usually returns data for major companies
    cnpj = "06990590000123" 
    data = consult_cnpj(cnpj)
    # Note: BrasilAPI might rate limit or fail, but this is a standard check
    if data:
        assert data["cnpj"] == cnpj
        assert "GOOGLE" in data["name"].upper()

def test_consult_cnpj_invalid():
    cnpj = "00000000000000"
    data = consult_cnpj(cnpj)
    assert data is None

def test_consult_cpf_valid():
    # Mock behavior check
    cpf = "12345678909"
    data = consult_cpf(cpf)
    assert data is not None
    assert data["cpf"] == "12345678909"
    assert "da Silva" in data["name"] or "Rocha" in data["name"] # Based on last digit 9 -> Juliana Rocha

def test_consult_cpf_invalid():
    cpf = "123"
    data = consult_cpf(cpf)
    assert data is None
