import unittest
from services.pricing import calculate_contract_totals

class TestPricing(unittest.TestCase):
    def test_calculate_totals_all_values_present(self):
        product = {
            'monthly_price': 100.0,
            'insurance_price': 50.0,
            'residual_value': 200.0
        }
        total, residual = calculate_contract_totals(product)
        self.assertEqual(total, 150.0)
        self.assertEqual(residual, 200.0)

    def test_calculate_totals_with_none_values(self):
        # This simulates the error condition the user faced
        product = {
            'monthly_price': 100.0,
            'insurance_price': None,
            'residual_value': None
        }
        total, residual = calculate_contract_totals(product)
        self.assertEqual(total, 100.0) # 100 + 0
        self.assertEqual(residual, 0.0)

    def test_calculate_totals_all_none(self):
        product = {
            'monthly_price': None,
            'insurance_price': None,
            'residual_value': None
        }
        total, residual = calculate_contract_totals(product)
        self.assertEqual(total, 0.0)
        self.assertEqual(residual, 0.0)

if __name__ == '__main__':
    unittest.main()
