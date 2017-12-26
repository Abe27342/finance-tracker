from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from json import load
from time import sleep


def click_button(driver, button_id):
	buttons = driver.find_elements_by_id(button_id)
	button = displayed_from_list(buttons)
	button.click()

def click_next_button(driver):
	click_button(driver, 'btnContinue')

def click_login_button(driver):
	click_button(driver, 'btnLogin')

def displayed_from_list(web_elements):
	for element in web_elements:
		if element.is_displayed():
			return element

def find_username(driver):
	usernames = driver.find_elements_by_name('personalId')
	return displayed_from_list(usernames)

def find_password(driver):
	# Totally a hack, but whatever. Element doesn't seem to have fully loaded if we don't have this...
	# even though a webdriver_wait should be sufficient, I can't get it to work. Odd.
	sleep(1) 
	passwords = driver.find_elements_by_id('txtPassword')
	return displayed_from_list(passwords)

def login(driver, webdriver_wait):
	credentials = load(open('Credentials/usbank.json', 'r'))
	driver.get(('https://onlinebanking.usbank.com/Auth/Login'))

	# fill in username and hit the next button
	username = find_username(driver)
	username.send_keys(credentials['username'])
	click_next_button(driver)
	# enter security questions
	security_box = webdriver_wait.until(
	   	EC.presence_of_element_located((By.NAME, 'txtAlphaNum'))
	   )

	question_credentials = credentials['security_questions']
	question_body = driver.find_element_by_xpath('//*[@id="dvLoginWidgetDir"]/form[2]/div[3]/div/div[1]/div/div[1]/label')
	security_box.send_keys(credentials['security_questions'][question_body.text])
	click_next_button(driver)

	webdriver_wait.until(EC.presence_of_element_located((By.NAME, 'password')))
	password = find_password(driver)
	password.send_keys(credentials['password'])
	click_login_button(driver)

def get_account_balance(driver, webdriver_wait):
	login(driver, webdriver_wait)
	account_balance = webdriver_wait.until(EC.presence_of_element_located((By.ID, 'DepositSpanHeaderTotal')))
	return account_balance.text


if __name__ == '__main__':
	from utils import get_driver, get_webdriver_wait
	driver = get_driver()
	webdriver_wait = get_webdriver_wait(driver)

	print get_account_balance(driver, webdriver_wait)
	driver.close()