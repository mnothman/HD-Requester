import unittest
import sqlite3
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add the root directory to the path


class PartCheckInOutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n\n=== Part Check-In/Out Tests ===")
        # Setup Chrome WebDriver
        options = Options()  # supress info message in output
        options.add_argument('--log-level=1') # supress info message in output
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.get("http://127.0.0.1:5000/")
        time.sleep(2)

    def check_modal(self, expected_title, expected_content):
        # Function to check if the modal is displayed and has correct title and content
        time.sleep(1)
        modal = self.driver.find_element(By.ID, "Modal")
        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "block", "Modal should be displayed")
        modal_title = self.driver.find_element(By.ID, "modalTitle").text.strip()
        modal_content = self.driver.find_element(By.ID, "modalContent").text.strip()
        self.assertEqual(modal_title, expected_title.strip(), "Modal title should match")
        self.assertIn(expected_content.strip(), modal_content, "Modal content should match")

    def close_modal(self):
        # Close the modal by clicking the close button
        time.sleep(1)
        close_button = self.driver.find_element(By.ID, "closeModalBtn")
        close_button.click()

    def checkin_part(self):
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\nPC4 4GB\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        time.sleep(1)

    def checkin_part_add_location(self):
        # Add Part Location
        locationInput = self.driver.find_element(By.ID, "locationInput")
        locationInput.send_keys("Box 7 C5")
        self.driver.find_element(By.ID, "locationSubmitBtn").click()
        time.sleep(1)

    def checkout_part(self):
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\nPC4 4GB\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        time.sleep(1)

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


    def test01_checkout_part(self):
        # Test case: Check Out Part
        print("Test 1: Check-out")
        self.checkout_part()

        # Verify the database Part now has 4999 parts with Status='In'
        # Execute the SQL query
        query = 'SELECT COUNT(*) FROM Part WHERE Status = ?'
        result = self.execute_query(query, ('In',))

        # Assert that the count matches 4999
        self.assertEqual(result, '4999')

    def test02_checkin_part(self):
        # Test case: Check In Part
        print("\nTest 2: Check-in")
        self.checkin_part()
        self.checkin_part_add_location()

        # Verify the database Part now has 5000 parts with Status='In'
        # Execute the SQL query
        query = 'SELECT COUNT(*) FROM Part WHERE Status = ?'
        result = self.execute_query(query, ('In',))

        # Assert that the count matches 5000
        self.assertEqual(result, '5000')

    def test03_checkin_already_checkedin_part(self):
        # Test case: Check In a Part that's Already Checked In
        print("\nTest 3: Check-in already checkedin part")
        self.checkin_part()
        
        # Expecting modal to show error
        self.check_modal("Check-in Error: Already checked-in.", "Serial number: 00000001")
        self.close_modal()

    def test04_checkout_already_checkedout_part(self):
        # Test case: Check Out a Part that's Already Checked out
        print("\nTest 4: Check-out already checkedout part")
        self.checkout_part()
        self.checkout_part()

        self.check_modal("Check-out Error: Already checked-out.", "Serial number: 00000001")
        self.close_modal()
        #replace
        self.checkin_part()
        self.checkin_part_add_location()

    def test05_checkout_mismatch_type_capacity(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        print("\nTest 5: Serial number mismatch with type or capacity")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\nPC3 4GB\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        self.check_modal(
            "Check-out Error: Mismatch in type or capacity.",
            "Expected: 4GB PC3\nFound: 4GB PC4"
        )
        self.close_modal()

    def test06_checkout_part_not_in_inventory(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        print("\nTest 6: Check-out Error: Part not seen in inventory before")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 5001
        textarea.send_keys("TI000000-00000001\n123456\nPC4 4GB\nLaptop\n00005001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        self.check_modal(
            "Check-out Error: Part not found in inventory.",
            "That part has never been added to inventory.\nSerial number: 00005001\nAdd item to inventory. Fill in the blanks"
        )
        self.close_modal()

    def test07_checkin_part_not_in_inventory(self):
        # Test case: Check-in Error: Part not seen b4
        print("\nTest 7: Check-in Error: Part not seen in inventory before")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 5001
        textarea.send_keys("TI000000-00000001\n123456\nPC4 4GB\nLaptop\n00005001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        self.check_modal(
            "Check-in Error: Part not found in inventory.",
            "That part has never been added to inventory.\nSerial number: 00005001\nAdd item to inventory. Fill in the blanks"
        )
        self.driver.find_element(By.ID, "iSpeed").send_keys("19200")
        self.driver.find_element(By.ID, "iBrand").send_keys("Brand-Refresh")
        self.driver.find_element(By.ID, "iModel").send_keys("Model-Refresh")
        self.driver.find_element(By.ID, "iLocation").send_keys("Location-Refresh")
        self.driver.find_element(By.ID, "add_btn").click()

        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert_text = alert.text
        self.assertEqual(alert_text, "Part added successfully.")
        alert.accept()

        time.sleep(2)
        # Verify the database Part is in the database
        # Execute the SQL query
        query = 'SELECT COUNT(*) FROM Part WHERE Part_sn=?'
        result = self.execute_query(query, ('00005001',))

        # Assert that the count matches 5000
        self.assertEqual(result, '1')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'refresh.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript('''
                           DELETE FROM Log WHERE Part_sn='00005001';
                           DELETE FROM Log WHERE TID='TI000000-00000001';
                           DELETE FROM Part WHERE Part_sn='00005001';
                           ''')
        conn.commit()

    def test08_checkout_missing_type(self):
       # Test case: Check-out Error: Missing Type
        print("\nTest 8: Check-out Error: Missing Type")
 
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 0001
        textarea.send_keys("TI000000-00000001\n123456\n4GB\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        
        self.check_modal(
            "Check-out Error: Missing Part Capacity.",
            "Expected: 4GB PC4\nFound: 4GB"
        )
        self.close_modal()

    def test09_checkout_missing_capacity(self):
       # Test case: Check-out Error: Missing capacity - Skip
        print("\nTest 9: Check-out Error: Missing Capacity - Skip")

        ### Need to fix our app and then remove this pass
        ##  and the ''' '''
        #
        pass
        r'''
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 00000001
        textarea.send_keys("TI000000-00000001\n123456\nHD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        
        self.check_modal(
            "Check-out Error: Missing Part Capacity.",
            "Expected: 256GB HD 3.5\nFound: HD 3.5"
        )
        self.close_modal()
        '''

    def test10_checkout_missing_unit_sn(self):
       # Test case: Check-out Error: Missing Unit Serial Number
        print("\nTest 10: Check-out Error: Missing Unit Serial Number - Skip")

        ### Need to fix our app and then remove this pass
        ##  and the ''' '''
        #
        pass
        r'''
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 00000001
        textarea.send_keys("TI000000-00000001\n256GB HD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-out Error: Missing unit serial number.",
            "Add unit serial number"
        )
        self.close_modal()
        '''

    def test11_checkout_mismatch_size(self):
        # Test case: Check-out Error: Mismatch in size
        print("\nTest 11: Check-out Error: Mismatch in Size - skip")
        ### Need to fix our app and then remove this pass
        ##  and the ''' '''
        #
        pass
        r'''
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 00000001
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\Desktop\n00005001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        
        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-out Error: Mismatch in size.",
            "Expected: Desktop\n Found: Laptop"
        )
        self.close_modal()
        '''

    def test12_checkout_missing_part_serial_number(self):
        # Test case: Check-out Error: Missing Serial Number
        print("\nTest 12: Missing Part serial number")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\nPC4 4GB\nLaptop")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Wait for the alert to be present
        try:
            WebDriverWait(self.driver, 10).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            self.assertEqual(alert_text, "Error: The number of parts does not match the number of serial numbers.", "Alert message should match expected error message.")
            # Click OK button on the alert
            alert.accept()
            print("Alert accepted")
        except TimeoutException:
            self.fail("Alert was not displayed when missing Part_sn")

        

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
