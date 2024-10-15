import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestAdminLoginCookie(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        # Disable headless mode if you want to see the browser interactions.
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.get("http://localhost:5000/login")  # Update to match your actual login page URL

        # Clear cookies to ensure no old cookies cause issues
        self.driver.delete_all_cookies()

    def test_remember_me_functionality(self):
        driver = self.driver

        # Step 1: Fill in the login form
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Step 2: Fill out the form with valid credentials
        username_input.send_keys("admin")  # Replace with valid username
        password_input.send_keys("admin123")  # Replace with valid password

        # Step 3: Check the "Remember Me" box
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        # Step 4: Submit the form (login)
        login_button.click()

        # Step 5: Wait for the redirect to complete and page to fully load
        WebDriverWait(driver, 10).until(EC.url_contains("/admin_dashboard"))

        # Step 6: Wait a bit longer to ensure cookies are set
        time.sleep(5)  # Allow additional time for cookies to be processed

        # Step 7: Verify the "remember_me" cookie is set
        cookies = driver.get_cookies()
        print("Cookies after login:", cookies)

        remember_me_cookie = None
        for cookie in cookies:
            if cookie['name'] == 'remember_me':
                remember_me_cookie = cookie
                break

        self.assertIsNotNone(remember_me_cookie, "The 'remember_me' cookie should be set after login.")
        self.assertEqual(remember_me_cookie['value'], "admin", "The 'remember_me' cookie should store the username.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
