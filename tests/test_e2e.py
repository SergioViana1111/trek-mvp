import pytest
from playwright.sync_api import Page, expect
import time

# Helper to handle Streamlit's iframe or finding elements
# Streamlit apps are often just one big root, but we can find input by label.

BASE_URL = "http://localhost:8503"

def test_full_user_flow(page: Page):
    # 1. Access Login Page
    page.goto(BASE_URL)
    
    # Check title
    expect(page).to_have_title("Trek - Celular por Assinatura", timeout=15000)
    
    # Wait for app to load (Streamlit often has a skeleton loader)
    time.sleep(3) 

    # Fill Login
    # Streamlit text_input often has aria-label matching the label
    page.get_by_label("Digite seu CPF").fill("11122233344")
    
    # Date Input
    # Streamlit date_input usually has a specific structure.
    # We can try to just type into the input if we find it.
    # Often it's the second input on the page if CPF is first.
    # Or matches label.
    
    # Debug: Print page content if needed (not in this env)
    # Let's try locating by the label text and then finding the input next to it.
    # Or just filling valid date string if the input accepts it.
    
    # Attempt: Target by aria-label if standard Streamlit
    # If get_by_label failed, it might be because the label isn't standard <label for=>.
    
    # Try generic fill by finding the input
    # Assuming CPF is first input, DOB is second.
    # page.locator("input").nth(1).fill("1995/05/20") # Dangerous if hidden inputs
    
    # More specific:
    # Look for the label text, then the input container.
    # date_input usually allows typing.
    dob_input = page.get_by_label("Data de Nascimento")
    # If get_by_label times out, it means it doesn't exist as an accessible label.
    
    # Fallback: Locate by visible text label near input
    # page.locator(":below(:text('Data de Nascimento'))").first...
    
    # Actually, let's try just typing into the specific input if we can identify it.
    # Streamlit Inputs usually have `aria-label` set to the label text.
    # Try explicit wait for the text to appear first.
    page.get_by_text("Data de Nascimento").wait_for()
    
    # If standard get_by_label failed, let's try clicking the Element that has the text 'Data de Nascimento' 
    # to focus, then tab to input? No.
    
    # Try locating the input by placeholder or just "input" type="text"
    # CPF is first text input. DOB is likely date or text.
    inputs = page.locator("input[type='text']")
    # CPF
    inputs.first.fill("11122233344")
    
    # DOB
    # Sometimes streamlit date input is two inputs (date/picker).
    # But usually one text input for value.
    # Let's try the second text input.
    if inputs.count() >= 2:
        inputs.nth(1).click()
        inputs.nth(1).fill("20/05/1995") # DD/MM/YYYY for Brazil
        inputs.nth(1).press("Enter")
    else:
        # Maybe it's type="date"?
        page.locator("input[type='date']").fill("1995-05-20")

    time.sleep(1) # Wait for UI update
    
    # Click Entrar
    page.get_by_role("button", name="Entrar").click()
    
    # Wait for redirect to Store
    # Store page title "Trek - Loja"
    expect(page).to_have_title("Trek - Loja", timeout=15000)
    
    # 2. Select a Phone (Samsung)
    time.sleep(2) # Wait for grid
    
    # Click "Escolher este"
    # If multiple, click first.
    btns = page.get_by_role("button", name="Escolher este")
    btns.first.wait_for()
    btns.first.click()
    
    # 3. Contract/Details Page
    expect(page).to_have_title("Trek - Contrato", timeout=15000)
    
    # Check details
    expect(page.get_by_text("Valor Residual:")).to_be_visible()
    
    # Terms
    # Checkbox
    page.get_by_role("checkbox", name="Li e concordo").check()
    
    # Fill Data
    # Wait for form
    expect(page.get_by_text("Seus Dados")).to_be_visible()
    
    # Inputs: Nome (0), Email (1), Celular (2), CEP(3), Endereço(4)...
    # Since we are inside a form, let's just find by label if possible, or Order.
    # "Endereço (Rua, Av)"
    page.get_by_label("Endereço (Rua, Av)").fill("Rua Teste 123")
    page.get_by_label("Número").fill("100")
    page.get_by_label("CEP").fill("12345-678")
    page.get_by_label("Celular").fill("11999999999")
    page.get_by_label("E-mail").fill("teste@email.com")
    
    # Submit
    page.get_by_role("button", name="Finalizar e Assinar Contrato").click()
    
    # 4. Success
    expect(page.get_by_text("Contrato assinado com sucesso!")).to_be_visible(timeout=20000)


def test_admin_flow(page: Page):
    page.goto(BASE_URL)
    time.sleep(3)
    
    # Login Admin
    inputs = page.locator("input[type='text']")
    inputs.first.fill("00000000000") # CPF
    
    # DOB
    if inputs.count() >= 2:
        inputs.nth(1).fill("01/01/1990")
        inputs.nth(1).press("Enter")
        
    page.get_by_role("button", name="Entrar").click()
    
    # Wait for Sidebar
    time.sleep(2)
    # Open Sidebar if collapsed? usually open on desktop.
    
    # Nav to Admin
    # Using generic text locator for sidebar link
    page.get_by_role("link", name="Admin").click()
    
    expect(page).to_have_title("Trek - Admin", timeout=15000)
    
    # Click Tab "Pedidos (Expedição)"
    page.get_by_text("Pedidos (Expedição)").click()
    time.sleep(1)
    
    # Dispatch
    # Look for button "Expedir"
    exp_btns = page.get_by_role("button", name="Expedir")
    
    if exp_btns.count() > 0:
        # Fill IMEI
        # We need the input associated with this button.
        # Streamlit doesn't nest them nicely.
        # But we can try filling the LAST text input if it's the one rendered for the item?
        # Or look for "IMEI" label.
        imei_inputs = page.get_by_label("IMEI")
        if imei_inputs.count() > 0:
            imei_inputs.first.fill("IMEI-TEST-PLAYWRIGHT")
            exp_btns.first.click()
            expect(page.get_by_text("Pedido expedido!")).to_be_visible(timeout=10000)
    else:
        print("No orders to dispatch.")

