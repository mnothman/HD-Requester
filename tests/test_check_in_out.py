import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class PartAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup Chrome WebDriver
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service)
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
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        time.sleep(1)

    def checkout_part(self):
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        time.sleep(1)


    def test01_checkout_part(self):
        # Test case: Check Out Part
        print("Test 1: Check-out")
        self.checkout_part()

        # Verify the database Part_log now has 4999 parts with Part_status='in'
        # Add database query here for verification
        #
        result = check_database_part_log_status('in', 4999)  # Mocked function for the example
        self.assertTrue(result, "There should be 4999 entities in the Part_log with Part_status='in'")

    def test02_checkin_part(self):
        # Test case: Check In Part
        print("\nTest 2: Check-in")
        self.checkin_part()

        # Verify the database Part_log now has 5000 parts with Part_status='in'
        result = check_database_part_log_status('in', 5000)  # Mocked function for the example
        self.assertTrue(result, "There should be 5000 entities in the Part_log with Part_status='in'")

    def test03_checkin_already_checkedin_part(self):
        # Test case: Check In a Part that's Already Checked In
        print("\nTest 3: Check-in already checkedin part")
        self.checkin_part()
        
        # Expecting modal to show error
        self.check_modal("Check-in Error: Already checked-in.", "Serial number: 00000001")
        self.close_modal()

    def test04_checkout_already_checkedout_part(self):
        # Test case: Check Out a Part that's Already Checked
        print("\nTest 4: Check-out already checkedout part")
        self.checkout_part()
        self.checkout_part()

        # Expecting modal to show error
        self.check_modal("Check-out Error: Already checked-out.", "Serial number: 00000001")
        self.close_modal()
        #replace
        self.checkin_part()

    def test05_checkout_mismatch_type_capacity(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        print("\nTest 5: Serial number mismatch with Type or Capacity")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000002")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-out Error: Mismatch in type or capacity.",
            "Expected: 256GB HD 3.5\nFound: 512GB PC4"
        )
        self.close_modal()

    def test06_checkout_part_not_in_inventory(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        print("\nTest 6: Check-out Error: Part not seen in inventory before")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 5001
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00005001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-out Error: Part not found in inventory.",
            "That part has never been added to inventory.\nSerial number: 00005001\nAdd item to inventory. Fill in the blanks"
        )
        self.close_modal()

    def test07_checkin_part_not_in_inventory(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        print("\nTest 7: Check-in Error: Part not seen in inventory before")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        # Using Serial number 5001
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00005001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-in Error: Part not found in inventory.",
            "That part has never been added to inventory.\nSerial number: 00005001\nAdd item to inventory. Fill in the blanks"
        )
        self.close_modal()

    def test08_checkout_drive_missing_type(self):
       pass

    def test09_checkin_missing_type_capacity(self):
        pass

    def test10_checkout_missing_unit_sn(self):
        pass

    def test11_checkin_missing_unit_sn(self):
        pass

    def test12_checkout_missing_part_serial_number(self):
        # Test case: Check-out Error: Missing Serial Number
        print("\nTest 12: Missing Part serial number")
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop")
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

# Mock function to simulate database check
def check_database_part_log_status(status, expected_count):
    # Placeholder for actual database query to count entities with a specific Part_status
    # 
    return True  # For the sake of the example, always return True

if __name__ == "__main__":
    unittest.main()
