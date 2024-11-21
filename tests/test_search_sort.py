import unittest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class PartSearchSortTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n\n=== Part Search/Sort Tests ===")
        options = Options()
        options.add_argument('--log-level=1')
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.implicitly_wait(10)

    def setUp(self):
        self.driver.get("http://127.0.0.1:8000/") 
    def test_search_functionality(self):
        print("Testing search functionality.")
        driver = self.driver

        # Locate the correct search input just below the other one
        search_input = driver.find_element(By.CSS_SELECTOR, "#partsTable_filter input[type='search']")  # Adjusted selector

        # Test 1: Searching for a known part
        search_input.clear()
        search_input.send_keys("SSD")
        search_input.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'SSD')]"))
        )
        table_rows = driver.find_elements(By.XPATH, "//table[@id='partsTable']//tbody//tr")
        self.assertTrue(len(table_rows) > 0, "Search for SSD should return at least one result.")
        print("Search for 'SSD' returned results as expected.")

        # Test 2: Searching for a non-existent part
        search_input.clear()
        search_input.send_keys("NonExistentPart")
        search_input.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'No matching records found')]"))
        )
        no_records_message = driver.find_element(By.XPATH, "//td[contains(text(), 'No matching records found')]")
        self.assertTrue(no_records_message.is_displayed(), "No matching records message should be displayed for non-existent parts.")
        print("Search for 'NonExistentPart' returned no results as expected.")

    # Commenting out the sorting functionality as requested
    def test_sorting_functionality(self):
        print("Testing sorting functionality.")
        driver = self.driver

        # Wait for the page to fully load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "partsTable"))
        )

        # Use JavaScript to trigger DataTables sorting on the 'Serial Number' column (7th column index for Serial Number)
        driver.execute_script("$('#partsTable').DataTable().order([7, 'asc']).draw();")

        # Wait for the sorting to complete by checking the updated sorting class
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//th[contains(@class, 'sorting_asc')]"))
        )

        # Fetch all rows from the Serial Number column after sorting
        part_sn_elements = driver.find_elements(By.XPATH, "//table[@id='partsTable']//tbody//tr/td[8]")

        # convert String to Integer for comparing serial numbers
        def alphanumeric_key(value):
            # Split into numeric and non-numeric parts
            return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', value)]


        # Collect the serial numbers from the column and verify sorting
        serial_numbers = [element.text for element in part_sn_elements]

        # Verify if the serial numbers are sorted in ascending order
        self.assertEqual(serial_numbers, sorted(serial_numbers, key=alphanumeric_key), "Serial numbers should be sorted in ascending order.")
        print("Sorting by 'Serial Number' column works as expected.")

        # Similarly, for the 'Type' column (0th index for Type column)
        driver.execute_script("$('#partsTable').DataTable().order([0, 'asc']).draw();")

        # Wait for the sorting to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//th[contains(@class, 'sorting_asc')]"))
        )

        # Fetch all rows from the 'Type' column and verify sorting
        type_elements = driver.find_elements(By.XPATH, "//table[@id='partsTable']//tbody//tr/td[1]")
        type_values = [element.text for element in type_elements]
    
        self.assertEqual(type_values, sorted(type_values), "'Type' column should be sorted in ascending order.")
        print("Sorting by 'Type' column works as expected.")



    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
