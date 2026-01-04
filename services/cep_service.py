import requests

def get_address_from_cep(cep: str) -> dict:
    """
    Fetches address information from BrasilAPI for a given CEP.
    
    Args:
        cep (str): The postal code to search (can include format symbols).
        
    Returns:
        dict: Address details (street, city, state, etc.) or None if not found/error.
    """
    # Remove non-numeric characters
    clean_cep = "".join(filter(str.isdigit, cep))
    
    if len(clean_cep) != 8:
        return None
        
    try:
        response = requests.get(f"https://brasilapi.com.br/api/cep/v2/{clean_cep}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Normalize keys to match our app usage if necessary, 
            # but BrasilAPI v2 returns: street, city, state, neighborhood, etc.
            return {
                "street": data.get("street"),
                "neighborhood": data.get("neighborhood"),
                "city": data.get("city"),
                "state": data.get("state"),
                "cep": clean_cep
            }
    except Exception as e:
        print(f"Error fetching CEP: {e}")
        return None
    
    return None
