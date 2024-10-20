import unittest 
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
        self.driver.get("http://127.0.0.1:5000/") 
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
    # def test_sorting_functionality(self):
    #     print("Testing sorting functionality.")
    #     driver = self.driver

    #     # Sort by the serial number column
    #     serial_column_header = driver.find_element(By.XPATH, "//th[contains(text(), 'Serial Number')]")
    #     serial_column_header.click()

    #     # Wait for sorting to finish (we assume that the first result changes or sorting arrow is updated)
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'sorting_asc')]"))
    #     )

    #     # Fetch the first and last part_sn values after sorting
    #     part_sn_elements = driver.find_elements(By.XPATH, "//table[@id='partsTable']//tbody//tr/td[1]")

    #     first_value = part_sn_elements[0].text
    #     last_value = part_sn_elements[-1].text

    #     # Assuming part_sn should be sorted alphabetically or numerically
    #     self.assertLessEqual(first_value, last_value, "The serial numbers should be sorted in ascending order.")
    #     print("Sorting by 'Serial Number' column works as expected.")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
