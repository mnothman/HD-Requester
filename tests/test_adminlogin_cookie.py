import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class AdminLoginCookieTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n\n=== Login Cookie Tests ===")
        chrome_options = Options()        
        # Use webdriver-manager to install and manage ChromeDriver
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.driver.get("http://127.0.0.1:8000/login")  # Replace with the actual login page URL

    def setUp(self):
        # Clear cookies before each test to avoid issues with old cookies
        self.driver.delete_all_cookies()

    def test_remember_me_functionality(self):
        driver = self.driver

        # Step 1: Ensure the login page is loaded
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        # Step 2: Fill in the login form
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Step 3: Fill out the form with valid credentials
        username_input.send_keys("admin")  # Replace with valid username
        password_input.send_keys("admin123")  # Replace with valid password

        # Step 4: Check the "Remember Me" box
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        # Step 5: Submit the form (login)
        login_button.click()

        # Step 6: Wait for the redirect to complete and page to fully load
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # Step 7: Verify the "remember_me" cookie is set
        cookies = driver.get_cookies()
        print("Cookies after login:", cookies)

        remember_me_cookie = next((cookie for cookie in cookies if cookie['name'] == 'remember_me'), None)
        self.assertIsNotNone(remember_me_cookie, "The 'remember_me' cookie should be set after login.")
        self.assertEqual(remember_me_cookie['value'], "admin", "The 'remember_me' cookie should store the username.")

    def test_without_remember_me(self):
        driver = self.driver

        # Step 1: Ensure the page is loaded before interacting
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        # Step 2: Fill in the login form
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Step 3: Fill out the form with valid credentials
        username_input.send_keys("admin")  # Replace with valid username
        password_input.send_keys("admin123")  # Replace with valid password

        # Step 4: Ensure the "Remember Me" box is NOT checked
        if remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        # Step 5: Submit the form (login)
        login_button.click()

        # Step 6: Wait for the redirect to complete and page to fully load
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # Step 7: Check that the "remember_me" cookie is NOT set
        cookies = driver.get_cookies()
        remember_me_cookie = next((cookie for cookie in cookies if cookie['name'] == 'remember_me'), None)
        self.assertIsNone(remember_me_cookie, "The 'remember_me' cookie should NOT be set when the checkbox is not selected.")

    def test_cookie_absent(self):
        driver = self.driver

        # Step 1: Ensure no cookies exist
        driver.delete_all_cookies()

        # Step 2: Reload the login page
        driver.get("http://localhost:5000/login")

        # Step 3: Verify that there are no cookies pre-set
        cookies = driver.get_cookies()
        self.assertEqual(len(cookies), 0, "No cookies should be present before login.")
        
        # Step 4: Verify the username field is not pre-filled
        pre_filled_username = driver.find_element(By.ID, "username").get_attribute("value")
        self.assertEqual(pre_filled_username, "", "Username should not be pre-filled when the Remember Me cookie is absent!")

    def test_cookie_after_logout(self):
        driver = self.driver

        # Step 1: Log in (without Remember Me)
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Enter credentials (without checking Remember Me)
        username_input.send_keys("admin")  # Replace with valid username
        password_input.send_keys("admin123")  # Replace with valid password
        login_button.click()

        # Step 2: Log out
        driver.get("http://localhost:5000/logout")

        # Step 3: Check remaining cookies after logout
        cookies = driver.get_cookies()
        print("Cookies after logging out:", cookies)

        # Step 4: If all cookies are deleted, update the assertion
        self.assertEqual(len(cookies), 0, "All cookies should be cleared after logout if Remember Me is not checked.")
    
    def test_cookie_persistence_across_sessions(self):
        driver = self.driver

        # Log in with "Remember Me"
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Enter credentials and select "Remember Me"
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # Save the cookies before quitting the browser
        cookies = driver.get_cookies()
        driver.quit()
        time.sleep(2)

        # Reopen the browser and set up again
        self.setUpClass()
        driver = self.driver  # Ensure we use the reopened driver instance

        # Restore the cookies
        driver.get("http://localhost:5000")  # Open any page to set cookies
        for cookie in cookies:
            driver.add_cookie(cookie)

        # Reload the login page and check if the "remember_me" cookie persists
        driver.get("http://localhost:5000/login")
        cookies = driver.get_cookies()

        remember_me_cookie = next((cookie for cookie in cookies if cookie['name'] == 'remember_me'), None)
        self.assertIsNotNone(remember_me_cookie, "The 'remember_me' cookie should persist across sessions.")

    def test_autofill_username_remember_me(self):
        driver = self.driver

        # Log in with "Remember Me"
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Enter credentials and select "Remember Me"
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # Log out and check auto-fill behavior
        driver.get("http://localhost:5000/logout")
        driver.get("http://localhost:5000/login")

        pre_filled_username = driver.find_element(By.ID, "username").get_attribute("value")
        self.assertEqual(pre_filled_username, "admin", "Username should be auto-filled after logging out with 'Remember Me'.")

    def test_invalid_credentials_remember_me(self):
        driver = self.driver

        # Load login page
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        # Enter invalid credentials
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys("invalid_user")
        password_input.send_keys("wrong_password")
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        login_button.click()

        # Ensure login fails and no cookies are set
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))  # Assuming it redirects back to login
        cookies = driver.get_cookies()
        remember_me_cookie = next((cookie for cookie in cookies if cookie['name'] == 'remember_me'), None)

        self.assertIsNone(remember_me_cookie, "No 'remember_me' cookie should be set for invalid login credentials.")

    def test_remember_me_cookie_expiry(self):
        driver = self.driver

        # Log in with "Remember Me"
        driver.get("http://localhost:5000/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        # Fill in credentials and select "Remember Me"
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        remember_me_checkbox = driver.find_element(By.ID, "rememberMe")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        if not remember_me_checkbox.is_selected():
            remember_me_checkbox.click()

        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))

        # Manually set cookie expiry to a past time
        driver.delete_cookie("remember_me")
        driver.add_cookie({
            'name': 'remember_me',
            'value': 'admin',
            'path': '/',
            'expiry': int(time.time()) - 1  # Use integer expiry time
        })

        # Reload page and verify that the "remember_me" cookie is no longer present
        driver.get("http://localhost:5000/login")
        cookies = driver.get_cookies()
        remember_me_cookie = next((cookie for cookie in cookies if cookie['name'] == 'remember_me'), None)
        self.assertIsNone(remember_me_cookie, "The 'remember_me' cookie should be removed after expiry.")

    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
