import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
        modal = self.driver.find_element(By.ID, "Modal")
        display_style = modal.value_of_css_property("display")
        self.assertEqual(display_style, "block", "Modal should be displayed")
        modal_title = self.driver.find_element(By.ID, "modalTitle").text.strip()
        modal_content = self.driver.find_element(By.ID, "modalContent").text.strip()
        self.assertEqual(modal_title, expected_title.strip(), "Modal title should match")
        self.assertIn(expected_content.strip(), modal_content, "Modal content should match")

    def close_modal(self):
        # Close the modal by clicking the close button
        close_button = self.driver.find_element(By.ID, "closeModalBtn")
        close_button.click()
        time.sleep(1)

    def checkin_part(self):
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnIn").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()

    def checkout_part(self):
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000001")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()


    def test01_checkout_part(self):
        # Test case: Check Out Part
        self.checkout_part()
        print("Check-out")

        # Verify the database Part_log now has 4999 parts with Part_status='in'
        # Add your database query here for verification (mocked or actual check)
        result = check_database_part_log_status('in', 4999)  # Mocked function for the example

        # replace
        self.checkin_part()

        self.assertTrue(result, "There should be 4999 entities in the Part_log with Part_status='in'")

    def test02_checkin_part(self):
        # Test case: Check In Part
        self.checkin_part()
        print("\nCheck-in")

        # Verify the database Part_log now has 5000 parts with Part_status='in'
        result = check_database_part_log_status('in', 5000)  # Mocked function for the example
        self.assertTrue(result, "There should be 5000 entities in the Part_log with Part_status='in'")

    def test03_checkin_already_checkedin_part(self):
        # Test case: Check In a Part that's Already Checked In
        self.checkin_part()
        
        # Expecting modal to show error
        self.check_modal("Check-in Error: Already checked-in.", "Serial number: 00000001")
        self.close_modal()
        print("\nCheck-in already checkedin part")
        print("\nClosed modal")
        time.sleep(2)

    def test04_checkout_already_checkedout_part(self):
        # Test case: Check Out a Part that's Already Checked 
        self.checkout_part()
        self.checkout_part()
        print("Check-out already checkedout part")
        time.sleep(2)

        # Expecting modal to show error
        self.check_modal("Check-out Error: Already checked-out.", "Serial number: 00000001")
        self.close_modal()
        print("Closed modal")
         #replace
        self.checkin_part()

    def test05_checkout_mismatch_type_capacity(self):
        # Test case: Check-out Error: Mismatch in type or capacity
        textarea = self.driver.find_element(By.ID, "textarea-request")
        textarea.clear()
        textarea.send_keys("TI000000-00000001\n123456\n256GB HD 3.5\nLaptop\n00000002")
        self.driver.find_element(By.ID, "btnOut").click()
        self.driver.find_element(By.ID, "btn-submit-request").click()
        print("Serial number mismatch with Type or Capacity")

        # Expecting modal to show mismatch error
        self.check_modal(
            "Check-out Error: Mismatch in type or capacity.",
            "<p><strong>Expected: </strong>256GB HD 3.5</p><p><strong>Found: </strong>512GB PC4</p>"
        )
        self.close_modal()
        print("Closed modal")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

# Mock function to simulate database check
def check_database_part_log_status(status, expected_count):
    # Placeholder for actual database query to count entities with a specific Part_status
    # You will implement the SQLite query here
    return True  # For the sake of the example, always return True

if __name__ == "__main__":
    unittest.main()
