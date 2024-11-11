import unittest
import sqlite3
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add the root directory to the path


class PartAddRemoveTests(unittest.TestCase):
    # global variable
    partsCount = 5000

    @classmethod
    def setUpClass(cls):
        print("\n\n=== Part Add/Remove Tests ===")
        # Setup Chrome WebDriver
        options = Options()  # supress info message in output
        options.add_argument('--log-level=1') # supress info message in output
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.get("http://127.0.0.1:8000/")


    def close_alert(self, expected_alert_text):
        # Close alert
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, expected_alert_text)

        # Wait briefly to ensure alert handling completes
        time.sleep(0.5)

    def add_part_btn(self):
        time.sleep(0.5)
        print("\n\n=== Checking Add Part Button... ===")

        button = self.driver.find_element(By.ID, "btnAddPart")
        button.click()

        print("\n\nClicked")

    def rmv_part_btn(self):
        time.sleep(0.5)
        print("\n\n=== Checking Remove Part Button... ===")

        button = self.driver.find_element(By.ID, "rmvPartBtn")
        button.click()

        print("\n\nClicked")


    def add_part_modal(self, expected_title):
        time.sleep(0.5)
        print("\n\n=== Checking modal title and content... ===")

        self.add_part_btn()

        modal_title = self.driver.find_element(By.ID, "modalTitle").text.strip()
        print(modal_title)

        self.assertEqual(modal_title, expected_title.strip(), "Modal title should match")
        print("Title matched")

    def add_part(self, sizeOption, serial_n):
        time.sleep(0.5)
        print(serial_n)
        
        self.add_part_btn()

        part_type = self.driver.find_element(By.ID, "iType")
        part_type.send_keys("HD 3.5")

        capacity = self.driver.find_element(By.ID, "iCapacity")
        capacity.send_keys("2TB")

        size = self.driver.find_element(By.ID, "ddSize")
        size_dropdown = Select(size)
        size_dropdown.select_by_visible_text(sizeOption)

        brand = self.driver.find_element(By.ID, "iBrand")
        brand.send_keys("Samsung")

        model = self.driver.find_element(By.ID, "iModel")
        model.send_keys("Model B")

        location = self.driver.find_element(By.ID, "iLocation")
        location.send_keys("Box 8 C5")

        part_sn = self.driver.find_element(By.ID, "iPart_sn")
        part_sn.send_keys(serial_n)

        # Add part with the information filled above
        ok_btn = self.driver.find_element(By.ID, "add_btn")
        ok_btn.click()

        print("Clicked ok for add part")

    def remove_part(self):
        last_page = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-dt-idx='6']"))
        )
        last_page.click()

        last_tr = self.driver.find_element("xpath", "//table[@id='partsTable']/tbody/tr[last()]")
        
        last_tr.click()

        self.rmv_part_btn()

        time.sleep(.5)

        confirm_btn = self.driver.find_element(By.ID, "confirmBtn")
        confirm_btn.click()


    def close_modal(self):
        # Close the modal by clicking the close button
        close_button = self.driver.find_element(By.ID, "closeModalBtn")
        close_button.click()

        print("\n\nClosed modal")

    def getPartsCount(self):
        query = 'SELECT COUNT(*) FROM Part WHERE Status = ?'
        partsCount = self.execute_query(query, ('In',))

        return partsCount


    
    ###################################
    ###################################
    ###################################

    def execute_query(self, query, params=()):
        """
        Connect to the SQLite database, execute a query, and return the result as a string.

        :param query: The SQL query to execute.
        :param params: The parameters to pass to the query (if any).
        :return: Query result as a string.
        """
        db_path = os.path.join(os.path.dirname(__file__), '..', 'refresh.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query with the provided parameters
        cursor.execute(query, params)
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Convert the result to a string or handle None if no result is found
        return str(result[0]) if result else "0"

    ###################################
    #########    TESTS    ############
    ###################################

    def test01_add_part_btn(self):
        print("\n\n === Test 1: Add Part Button ===\n")
        self.add_part_btn()
        self.close_modal()

    def test02_add_part_modal(self):
        print("\n\n === Test 2: Check Modal ===\n")
        self.add_part_modal("Add New Part")
        self.close_modal()

    def test03_add_part(self):
        print("\n\n === Test 3: Add Part with 4 different sizes ===\n")

        # Error occurred:  UNIQUE constraint failed: Part.Part_sn
        self.add_part("Desktop", "00005001")
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part added successfully.")
        alert.accept()
        
        '''
        self.add_part("Laptop", "00005002")
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part added successfully.")
        alert.accept()

        self.add_part('2.5" HD', "00005003")
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part added successfully.")
        alert.accept()

        self.add_part('3.5" HD', "00005004")
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part added successfully.")
        alert.accept()
        '''
    def test04_remove_part_no_selection(self):
        print("\n\n === Test 4: Remove Part - No Selection ===\n")

        time.sleep(1)

        self.rmv_part_btn()

        # Close the alert - Successful or error request
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "No parts selected for removal.")
        alert.accept()


    def test05_remove_part_selection(self):
        print("\n\n === Test 4: Remove Part ===\n")

        parts_count = self.getPartsCount()

        print(parts_count)

        self.remove_part()

        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "All selected parts have been marked as deleted.")
        
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        # Set up the database connection
        db_path = os.path.join(os.path.dirname(__file__), '..', 'refresh.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Define the queries
        query1 = "DELETE FROM Log WHERE Part_sn = ?"
        query2 = "DELETE FROM Part WHERE Part_sn = ?"

        # Execute each query with the parameter
        cursor.execute(query1, ('00005001',))
        cursor.execute(query2, ('00005001',))

        # Commit the transaction
        conn.commit()

        # Close the database connection
        conn.close()

        # Quit the driver
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()