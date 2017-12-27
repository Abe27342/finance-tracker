from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import abstractmethod, abstractproperty
from utils import pennies_from_text

class WebScraper:
	"""
	Simple abstract base class for a website scraper which we will pull 
	financial data with. Given a selenium driver to initialize (and waiter),
	it provides an API to get the account balance for that website.
	"""
	def __init__(self, driver, webdriver_wait, credentials):
		"""
		Args:
		    driver (selenium.WebDriver): Selenium web driver to use to scrape.
		    webdriver_wait (selenium.WebDriverWait): Wait driver for scraping.
		    credentials (Credentials): Credential information for any login required.
		"""
		self._driver = driver
		self._webdriver_wait = webdriver_wait
		self._credentials = credentials

	@abstractmethod
	def _find_password_field(self):
		pass

	@abstractmethod
	def _find_username_field(self):
		pass

	@abstractmethod
	def _login(self):
		pass

	@abstractmethod
	def get_account_balance(self):
		"""
		Returns:
		    int: Account balance in pennies
		"""
		pass

class SimpleLoginScraper(WebScraper):
	"""
	WebScraper for a website which has a single authentication page that works via
	supplying the credentials and pressing enter.
	"""
	def _login(self):
		driver.get((self._login_url))

		# fill in username and hit the next button
		username_field = self._find_username_field()
		username_field.send_keys(self._credentials.username)
		password_field = self._find_password_field()
		password_field.send_keys(self._credentials.password)
		password_field.send_keys(Keys.ENTER)

	@abstractproperty
	def _login_url(self):
		"""
		Returns:
		    str: The url for the login page.
		"""
		pass

class VanguardScraper(SimpleLoginScraper):
	def _find_password_field(self):
		return self._driver.find_element_by_name('PASSWORD')

	def _find_username_field(self):
		return self._driver.find_element_by_name('USER')

	@property
	def _login_url(self):
		return 'https://investor.vanguard.com/my-account/log-on'

	def get_account_balance(self):
		self._login()
		account_balance = self._webdriver_wait.until(
		    EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[1]/span'))
		    )
		return pennies_from_text(account_balance.text)

class AllyScraper(SimpleLoginScraper):
	def _find_password_field(self):
		return self._driver.find_element_by_id('login-password')

	def _find_username_field(self):
		return self._driver.find_element_by_id('login-username')

	@property
	def _login_url(self):
		return 'https://secure.ally.com/'

	def get_account_balance(self):
		self._login()
		account_balance = self._webdriver_wait.until(
		    EC.presence_of_element_located((By.XPATH, '//*[@id="ember2248"]/tfoot/td[1]'))
		    )
		return pennies_from_text(account_balance.text)

class FidelityScraper(SimpleLoginScraper):
	def _find_password_field(self):
		return self._driver.find_element_by_id('password')

	def _find_username_field(self):
		return self._driver.find_element_by_id('userId-input')

	@property
	def _login_url(self):
		return 'https://oltx.fidelity.com/ftgw/fbc/ofsummary/defaultPage'

	def get_account_balance(self):
		self._login()
		account_balance = self._webdriver_wait.until(
			EC.presence_of_element_located((By.CSS_SELECTOR,
			'body > div.fidgrid.fidgrid--shadow.fidgrid--nogutter > div.full-page--container > div.fidgrid--row.port-summary-container > div.port-summary-content.clearfix > div:nth-child(2) > div.fidgrid--content > div > div.account-selector-wrapper.port-nav.account-selector--reveal > div.account-selector.account-selector--normal-mode.clearfix > div.account-selector--main-wrapper > div.account-selector--accounts-wrapper > div.account-selector--tab.account-selector--tab-all.js-portfolio.account-selector--target-tab.js-selected > span.account-selector--tab-row.account-selector--all-accounts-balance.js-portfolio-balance'))
		)
		return pennies_from_text(account_balance.text)

# The US bank website has a more annoying log on process, so it doesn't get simple log in :(
class USBankScraper(WebScraper):
	def _click_button(self, button_id):
		buttons = self._driver.find_elements_by_id(button_id)
		button = next(button for button in buttons if button.is_displayed())
		button.click()

	def _click_next_button(self):
		self._click_button('btnContinue')

	def _click_login_button(self):
		self._click_button('btnLogin')

	def _find_password_field(self):
		password = self._webdriver_wait.until(EC.presence_of_element_located((By.NAME, 'password')))
		# With the way USBank loads the webpage, it seems the password field appears before it is visible.
		return self._webdriver_wait.until(EC.visibility_of(password))

		# _driver.find_element_by_name('password')

	def _find_username_field(self):
		return self._driver.find_element_by_name('personalId')

	def _login(self):
		driver.get(('https://onlinebanking.usbank.com/Auth/Login'))

		# fill in username and hit the next button
		username_field = self._find_username_field()
		username_field.send_keys(self._credentials.username)
		self._click_next_button()
		# enter security questions
		security_box = self._webdriver_wait.until(
		   	EC.presence_of_element_located((By.NAME, 'txtAlphaNum'))
		   )

		question = self._driver.find_element_by_xpath('//*[@id="dvLoginWidgetDir"]/form[2]/div[3]/div/div[1]/div/div[1]/label')
		security_box.send_keys(self._credentials.answer_security_question(question.text))
		self._click_next_button()
		password_field = self._find_password_field()
		password_field.send_keys(self._credentials.password)
		self._click_login_button()

	def get_account_balance(self):
		self._login()
		account_balance = webdriver_wait.until(EC.presence_of_element_located((By.ID, 'DepositSpanHeaderTotal')))
		return pennies_from_text(account_balance.text)
		

if __name__ == '__main__':
	from utils import get_driver, get_webdriver_wait
	from credentials import JSONCredentials

	driver = get_driver()
	webdriver_wait = get_webdriver_wait(driver)

	my_pennies = 0

	credentials = JSONCredentials(''.join(open('Credentials/USBank.json', 'r').readlines()))
	scraper = USBankScraper(driver, webdriver_wait, credentials)
	us_bank_pennies = scraper.get_account_balance()
	print "US bank account balance: %s" % us_bank_pennies

	credentials = JSONCredentials(''.join(open('Credentials/vanguard.json', 'r').readlines()))
	scraper = VanguardScraper(driver, webdriver_wait, credentials)
	vanguard_pennies = scraper.get_account_balance()
	print "Vanguard account balance: %s" % vanguard_pennies

	credentials = JSONCredentials(''.join(open('Credentials/ally.json', 'r').readlines()))
	scraper = AllyScraper(driver, webdriver_wait, credentials)
	ally_pennies = scraper.get_account_balance()
	print "Ally account balance: %s" % ally_pennies

	credentials = JSONCredentials(''.join(open('Credentials/fidelity.json', 'r').readlines()))
	scraper = FidelityScraper(driver, webdriver_wait, credentials)
	fidelity_pennies = scraper.get_account_balance()
	print "Fidelity account balance: %s" % fidelity_pennies

	print "Total money: $%s" % ((us_bank_pennies + vanguard_pennies + ally_pennies + fidelity_pennies) / 100.0)
	driver.close()