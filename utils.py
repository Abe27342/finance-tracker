from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

def get_driver():
	options = Options()

	# Would eventually like to use this line, but it makes various auth sites think
	# the browser has a different identity and I don't want to automate more security
	# questions (when I shouldn't have to...)
	# options.add_argument('headless')
	# ... so instead I'll use this one ;)
	options.add_argument('--window-position=-32000,-32000')
	driver = webdriver.Chrome(options=options)
	driver.set_window_size(1920, 1080)
	driver.implicitly_wait(1)
	return driver

def get_webdriver_wait(driver):
	return WebDriverWait(driver, 10)