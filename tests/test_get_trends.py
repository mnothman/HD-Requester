from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import requests
import unittest

class FlaskEndpointTest(unittest.TestCase):
    def setUp(cls):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=1') # supress info message in output
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.base_url = "http://127.0.0.1:8000"
        print("\n\n=== Get Trends Test ===")
        time.sleep(1)


    def test_get_trends(self):
        endpoint = f"{self.base_url}/get_trends?month=10&year=2024"
        response = requests.get(endpoint)
        
        # Ensure request is successful
        self.assertEqual(response.status_code, 200, "Expected status code 200, but got {}".format(response.status_code))
        
        response_data = response.json()
        
        # Expected data for specific dates
        expected_data_subset = {
            "2024-10-01": {"check_ins": 2, "check_outs": 5, "desktop_transactions": 3, "laptop_transactions": 3},
            "2024-10-02": {"check_ins": 5, "check_outs": 7, "desktop_transactions": 3, "laptop_transactions": 2},
            "2024-10-03": {"check_ins": 3, "check_outs": 3, "desktop_transactions": 0, "laptop_transactions": 0}
        }
        
        # Check response contains expected data for specific dates
        for date, expected_values in expected_data_subset.items():
            self.assertIn(date, response_data["data"], f"Expected date '{date}' not found in response data.")
            self.assertDictEqual(response_data["data"][date], expected_values, f"Data for date '{date}' does not match expected values.")
        
        # Check status
        self.assertEqual(response_data["status"], "success", "Expected status 'success', but got '{}'".format(response_data["status"]))


    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
