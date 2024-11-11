import unittest
import sqlite3
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add the root directory to the path


class EditPartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n\n=== Edit Part Tests ===")
        # Setup Chrome WebDriver
        options = Options()  # supress info message in output
        options.add_argument('--log-level=1') # supress info message in output
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.get("http://127.0.0.1:8000/")
        time.sleep(2)


    @classmethod
    def execute_query(self, query, params=()):
        db_path = os.path.join(os.path.dirname(__file__), '..', 'refresh.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query with the provided parameters
        cursor.execute(query, params)
        
        # If the query is a SELECT, fetch and return the result
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchone()
            conn.close()
            return str(result[0]) if result else "0"
        else:
            # For non-SELECT queries, commit the transaction
            conn.commit()
            conn.close()


    def check_modal(self, expected_title, expected_content):
        # Function to check if the modal is displayed and has correct title and content
        time.sleep(1)
        modal = self.driver.find_element(By.XPATH, "//*[contains(@id, 'Modal')]")
        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "block", "Modal should be displayed")
        modal_title = self.driver.find_element(By.ID, "modalTitle").text.strip()
        modal_content = self.driver.find_element(By.ID, "modalContent").text.strip()
        self.assertEqual(modal_title, expected_title.strip(), "Modal title should match")
        self.assertIn(expected_content.strip(), modal_content, "Modal content should match")

    def close_modal(self):
        # Close the modal by clicking the close button
        # Wait for the close button to be clickable
        close_button = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.ID, "closeModalBtn"))
        )
        self.driver.execute_script("arguments[0].click();", close_button)


    def right_click_edit(self):
        # Locate the row that has a part with serial number 00000002
        part_sn_2 = self.driver.find_element(By.XPATH, "//td[contains(text(), '00000002')]")

        # Perform right-click
        self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('contextmenu', {bubbles: true}));", part_sn_2)
        
        # Wait for the context menu to appear and locate the 'edit' option
        try:
            edit_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.context-menu li.edit"))
            )
            edit_option.click()
            time.sleep(1)
        except TimeoutException:
            print("Edit option not found in context menu.")


    def edit_part_change_details(self):
        inputCapacity = self.driver.find_element(By.ID, "editCapacity")
        inputCapacity.clear()  # Clear existing value
        inputCapacity.send_keys("2TB")
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save Changes')]")
        save_button.click()


    def test01_edit_part_modal_close(self):
        print("\nTest 1: Close Modal Edit Part")
        
        modal = self.driver.find_element(By.XPATH, "//*[contains(@id, 'Modal')]")

        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "none", "Modal should not be displayed")
        self.right_click_edit()

        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "block", "Modal should be displayed")

        self.close_modal()

        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "none", "Modal should not be displayed")


    def test02_edit_part(self):
        # Test case: Edit Part
        print("\nTest 2: Edit Part")

        # prepare our tests by making the capacity 1TB
        query = 'UPDATE Part SET Capacity = ? WHERE Part_sn = ?'
        self.execute_query(query, ('1TB', '00000002'))


        query = 'SELECT Capacity FROM Part WHERE Part_sn = ?'
        
        # Fetch the Capacity before editing
        capacity_before = self.execute_query(query, ('00000002',))

        # Perform the edit operation
        self.right_click_edit()
        self.edit_part_change_details()

        # Wait for and handle the alert
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part updated successfully")
        alert.accept()

        # Fetch the Capacity after editing
        capacity_after = self.execute_query(query, ('00000002',))

        # Assert that the Capacity has changed as expected
        self.assertNotEqual(capacity_before, capacity_after, "Capacity should be updated")
        self.assertEqual(capacity_after, "2TB", "Capacity should be updated to '2TB'")
        time.sleep(2)
        # Check Log records
        query = 'SELECT Note FROM Log ORDER BY Date_time DESC LIMIT 1'
        note = self.execute_query(query)
        self.assertEqual(note, "capacity changed from '1TB' to '2TB'")

    @classmethod
    def tearDownClass(cls):
        query_1TB = "UPDATE Part SET Capacity = '1TB' WHERE Part_sn = '00000002'"
        query_delete = 'DELETE FROM Log WHERE Date_time = (SELECT Date_time FROM Log ORDER BY Date_time DESC LIMIT 1);'
        cls.execute_query(query_1TB)
        cls.execute_query(query_delete)
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
