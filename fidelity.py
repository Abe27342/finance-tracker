from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from json import load
from time import sleep

def find_password(driver):
	return driver.find_element_by_id('password')

def find_username(driver):
	return driver.find_element_by_id('userId-input')

def login(driver, webdriver_wait):
	credentials = load(open('Credentials/fidelity.json', 'r'))
	driver.get(('https://oltx.fidelity.com/ftgw/fbc/ofsummary/defaultPage'))

	# fill in username and hit the next button
	element = find_username(driver)
	element.send_keys(credentials['username'])
	element = find_password(driver)
	element.send_keys(credentials['password'])
	element.send_keys(Keys.ENTER)

def get_account_balance(driver, webdriver_wait):
	login(driver, webdriver_wait)
	account_balance = webdriver_wait.until(
		EC.presence_of_element_located((By.CSS_SELECTOR,
			'body > div.fidgrid.fidgrid--shadow.fidgrid--nogutter > div.full-page--container > div.fidgrid--row.port-summary-container > div.port-summary-content.clearfix > div:nth-child(2) > div.fidgrid--content > div > div.account-selector-wrapper.port-nav.account-selector--reveal > div.account-selector.account-selector--normal-mode.clearfix > div.account-selector--main-wrapper > div.account-selector--accounts-wrapper > div.account-selector--tab.account-selector--tab-all.js-portfolio.account-selector--target-tab.js-selected > span.account-selector--tab-row.account-selector--all-accounts-balance.js-portfolio-balance'))
		)
	return account_balance.text


if __name__ == '__main__':
	from utils import get_driver, get_webdriver_wait
	driver = get_driver()
	webdriver_wait = get_webdriver_wait(driver)

	print get_account_balance(driver, webdriver_wait)
	driver.close()
