from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("http://127.0.0.1:5000/")

input_element = driver.find_element(By.ID, "textarea-request")
input_element.send_keys("TI000001-00000001" + Keys.ENTER)
input_element.send_keys("123456" + Keys.ENTER)
input_element.send_keys("256GB HD 3.5" + Keys.ENTER)
input_element.send_keys("Laptop" + Keys.ENTER)
input_element.send_keys("00000001" + Keys.ENTER)

input_element = driver.find_element(By.ID, "btnradio2")
input_element.click()

input_element = driver.find_element(By.ID, "btn-submit-request")
input_element.click()

time.sleep(10)

driver.quit()