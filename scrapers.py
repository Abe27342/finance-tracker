from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from abc import abstractmethod, abstractproperty
from utils import pennies_from_text
from time import sleep

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
        self._driver.get((self._login_url))

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
        try:
            # Vanguard puts up holiday warnings sometimes.
            button = self._webdriver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#continueInput')))
            button.click()
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

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

class text_has_loaded(object):
    """ An expectation for checking if the given text is present in the
    specified element.
    locator, text
    """
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).text
            return len(element_text) > 0
        except StaleElementReferenceException:
            return False

class PremeraScraper(SimpleLoginScraper):
    def _find_password_field(self):
        return self._driver.find_element_by_id('Password')

    def _find_username_field(self):
        return self._driver.find_element_by_id('LoginId')

    @property
    def _login_url(self):
        return 'https://www.premera.com/portals/member/account/logon'

    def get_account_balance(self):
        self._login()
        personal_funding_account = self._webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#toggle1 > li:nth-child(5) > a')))
        self._webdriver_wait.until(EC.visibility_of(personal_funding_account))
        personal_funding_account.click()
        sleep(1)
        manage_your_account = self._webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#content-main > p:nth-child(4) > a')))
        self._webdriver_wait.until(EC.visibility_of(manage_your_account))
        orig_tab = self._driver.window_handles[0]
        manage_your_account.click()
        sleep(1)
        for tab in self._driver.window_handles:
            if tab != orig_tab:
                new_tab = tab

        self._driver.switch_to_window(new_tab)
        self._webdriver_wait.until(text_has_loaded((By.ID, 'totalValue')))
        account_balance = self._driver.find_element_by_id('totalValue')
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
        # With the way USBank loads the webpage, it seems the password field gets located before it is visible.
        return self._webdriver_wait.until(EC.visibility_of(password))

    def _find_username_field(self):
        return self._driver.find_element_by_name('personalId')

    def _login(self):
        self._driver.get(('https://onlinebanking.usbank.com/Auth/Login'))

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
        account_balance = self._webdriver_wait.until(EC.presence_of_element_located((By.ID, 'DepositSpanHeaderTotal')))
        return pennies_from_text(account_balance.text)