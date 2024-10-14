import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AdminLoginTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument('--log-level=1')
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.implicitly_wait(10)  # Wait for elements to appear

    def setUp(self):
        self.driver.get("http://127.0.0.1:5000/login")  # Ensure starting from login page for each test

    def test_password_recovery_incorrect_answer(self):
        # Simulate password recovery with incorrect security answers
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "forgotPass"))
        ).click()
        time.sleep(2)  # Ensure the transition to recovery form is complete
        self.driver.find_element(By.ID, "security-answer1").send_keys("wrong_team")
        self.driver.find_element(By.ID, "security-answer2").send_keys("wrong_pet")
        self.driver.find_element(By.ID, "security-answer3").send_keys("wrong_vacation")
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#form-recover-password button[type='submit']"))
        )
        submit_button.click()
        time.sleep(2)

    def test_password_recovery_empty_answers(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "forgotPass"))
        ).click()
        time.sleep(2)  # Ensure the transition to recovery form is complete
        self.driver.find_element(By.ID, "security-answer1").clear()
        self.driver.find_element(By.ID, "security-answer2").clear()
        self.driver.find_element(By.ID, "security-answer3").clear()
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#form-recover-password button[type='submit']"))
        )
        submit_button.click()
        time.sleep(2)

    def test_login_with_valid_credentials(self):
        # Test login with correct admin credentials
        self.driver.find_element(By.ID, "username").send_keys("admin")
        self.driver.find_element(By.ID, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

    def test_login_with_incorrect_password(self):
        # Test login with incorrect password
        self.driver.find_element(By.ID, "username").send_keys("admin")
        self.driver.find_element(By.ID, "password").send_keys("wrong_password")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

    def test_login_with_empty_password(self):
        # Test login with empty password field
        self.driver.find_element(By.ID, "username").send_keys("admin")
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
