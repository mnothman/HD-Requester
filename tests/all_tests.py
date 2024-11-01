# all_tests.py
import unittest
import subprocess
import sys

# Check for webdriver_manager installation
try:
    import webdriver_manager
except ModuleNotFoundError:
    install = input("webdriver_manager is not installed. Do you want to install it? (y/n): ").strip().lower()
    if install == 'y':
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver_manager"])
        print("webdriver_manager installed successfully.")
    else:
        print("webdriver_manager is required to run these tests. Exiting.")
        sys.exit(1)

# Import test cases
import test_admin_login
import test_adminlogin_cookie
import test_check_in_out
import test_add_or_remove_part
import test_edit_part
import test_search_sort

# Create a test suite combining tests from multiple files
def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()  # Create a TestLoader instance

    # Add test cases from each file using loadTestsFromTestCase
    suite.addTests(loader.loadTestsFromTestCase(test_admin_login.AdminLoginTests))
    suite.addTests(loader.loadTestsFromTestCase(test_adminlogin_cookie.AdminLoginCookieTests))
    suite.addTests(loader.loadTestsFromTestCase(test_check_in_out.PartCheckInOutTest))
    suite.addTests(loader.loadTestsFromTestCase(test_add_or_remove_part.PartAddRemoveTests))
    suite.addTests(loader.loadTestsFromTestCase(test_edit_part.EditPartTests))
    suite.addTests(loader.loadTestsFromTestCase(test_search_sort.PartSearchSortTests))

    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
