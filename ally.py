from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from json import load
from time import sleep

def find_password(driver):
	return driver.find_element_by_id('login-password')

def find_username(driver):
	return driver.find_element_by_id('login-username')

def login(driver, webdriver_wait):
	credentials = load(open('Credentials/ally.json', 'r'))
	driver.get(('https://secure.ally.com/'))

	element = find_username(driver)
	element.send_keys(credentials['username'])
	element = find_password(driver)
	element.send_keys(credentials['password'])
	element.send_keys(Keys.ENTER)

def get_account_balance(driver, webdriver_wait):
	login(driver, webdriver_wait)
	driver.save_screenshot('after_login.png')
	account_balance = webdriver_wait.until(
		EC.presence_of_element_located((By.XPATH, '//*[@id="ember2248"]/tfoot/td[1]'))
		)

	return account_balance.text

if __name__ == '__main__':
	from utils import get_driver, get_webdriver_wait
	driver = get_driver()
	webdriver_wait = get_webdriver_wait(driver)

	print get_account_balance(driver, webdriver_wait)
	driver.close()
