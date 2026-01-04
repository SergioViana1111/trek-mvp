import requests
import datetime

def consult_cnpj(cnpj: str) -> dict:
    """
    Fetches company data from BrasilAPI.
    Args:
        cnpj (str): The CNPJ to search.
    Returns:
        dict: Company details (name, address, etc.) or None.
    """
    clean_cnpj = "".join(filter(str.isdigit, cnpj))
    if len(clean_cnpj) != 14:
        return None
        
    try:
        response = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{clean_cnpj}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            address_parts = [
                data.get("logradouro"),
                data.get("numero"),
                data.get("complemento"),
                data.get("bairro"),
                data.get("municipio"),
                data.get("uf"),
                f"CEP: {data.get('cep')}"
            ]
            full_address = ", ".join([p for p in address_parts if p])
            
            return {
                "name": data.get("razao_social") or data.get("nome_fantasia"),
                "address": full_address,
                "cnpj": clean_cnpj
            }
    except Exception as e:
        print(f"Error fetching CNPJ: {e}")
        return None
    return None

def consult_cpf(cpf: str) -> dict:
    """
    Mocks fetching person data from CPF.
    In a real scenario, this would connect to Serpro or Dataprev.
    Args:
        cpf (str): The CPF to search.
    Returns:
        dict: Person details (name, birth_date) or None.
    """
    clean_cpf = "".join(filter(str.isdigit, cpf))
    if len(clean_cpf) != 11:
        return None
    
    # Mock data based on last digit for variety
    last_digit = int(clean_cpf[-1])
    
    names = [
        "João da Silva", "Maria Oliveira", "Pedro Santos", "Ana Costa", 
        "Carlos Pereira", "Beatriz Souza", "Lucas Ferreira", "Fernanda Lima",
        "Rafael Almeida", "Juliana Rocha"
    ]
    
    # Deterministic mock based on CPF
    name = names[last_digit]
    
    # Random-ish date
    year = 1980 + last_digit
    month = max(1, last_digit)
    day = max(1, last_digit * 2)
    birth_date = datetime.date(year, month, day)
    
    return {
        "name": name,
        "birth_date": birth_date,
        "cpf": clean_cpf
    }
