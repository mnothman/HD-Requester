import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class PartSortingAndSearchingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--log-level=1')
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.get("http://127.0.0.1:5000/")  #
        cls.driver.implicitly_wait(10)

    def test_sort_all_columns(self):
        headers = self.driver.find_elements(By.CSS_SELECTOR, "#partsTable th")
        for header in headers:
            column_name = header.text
            # Skip if the header is not meant to be sortable
            if not column_name.strip():
                continue

            # Click to sort ascending
            header.click()
            time.sleep(2)  # Allow time for sorting to take effect
            self.check_sorting(column_name, 'ascending')

            # Click to sort descending
            header.click()
            time.sleep(2)  # Allow time for sorting to take effect
            self.check_sorting(column_name, 'descending')

    def check_sorting(self, column_name, order):
        # Navigate to the first page and grab the first character of the first row
        self.driver.find_element(By.LINK_TEXT, "1").click()
        time.sleep(2)
        first_row_text = self.driver.find_element(By.CSS_SELECTOR, "#partsTable tbody tr:first-child td.sorting_1").text

        # Navigate to the last page and grab the first character of the last row
        self.driver.find_element(By.LINK_TEXT, "500").click()
        time.sleep(2)
        last_row_text = self.driver.find_element(By.CSS_SELECTOR, "#partsTable tbody tr:last-child td.sorting_1").text

        # Verify alphabetical order based on sort direction
        if order == 'ascending':
            assert first_row_text <= last_row_text, f"Column '{column_name}' should be sorted in ascending order"
        else:
            assert first_row_text >= last_row_text, f"Column '{column_name}' should be sorted in descending order"

        # Reset to page 1
        self.driver.find_element(By.LINK_TEXT, "1").click()
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
