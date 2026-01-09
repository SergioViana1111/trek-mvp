def calculate_contract_totals(product: dict):
    """
    Calculates the total monthly value and residual value for a product,
    safely handling None/Null values by defaulting them to 0.0.
    
    Args:
        product (dict): The product dictionary containing 'monthly_price', 
                        'insurance_price', and 'residual_value'.
                        
    Returns:
        tuple: (total_monthly, residual_value)
    """
    # Safe float conversion handling None or empty strings
    p_monthly = float(product.get('monthly_price') or 0)
    p_insurance = float(product.get('insurance_price') or 0)
    
    total_monthly = p_monthly + p_insurance
    residual = float(product.get('residual_value') or 0)
    
    return total_monthly, residual
