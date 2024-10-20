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


class PartAddRemoveTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n\n=== Part Add/Remove Tests ===")
        # Setup Chrome WebDriver
        options = Options()  # supress info message in output
        options.add_argument('--log-level=1') # supress info message in output
        cls.service = Service(executable_path="chromedriver.exe")
        cls.driver = webdriver.Chrome(service=cls.service, options=options)
        cls.driver.get("http://127.0.0.1:5000/")
        time.sleep(2)


    def add_part(self):
        pass
    

    def remove_part(self):
        pass


    
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
    #########     TESTS    ############
    ###################################

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()