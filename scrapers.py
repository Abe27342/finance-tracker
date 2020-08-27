from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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
        sleep(5)
        # fill in username and hit the next button
        username_field = self._find_username_field()
        username_field.send_keys(self._credentials.username)
        sleep(2)
        password_field = self._find_password_field()
        password_field.send_keys(self._credentials.password)
        sleep(2)
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
        return self._driver.find_element_by_id('password')

    def _find_username_field(self):
        return self._driver.find_element_by_id('username')

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
            EC.presence_of_element_located((By.XPATH, '//*[@id="balances"]/div/div[3]/div[2]/span'))
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
            EC.presence_of_element_located((By.CSS_SELECTOR, '.total.stat'))
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
        sleep(5)
        self._driver.get(('https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#balances'))

        account_balance = self._webdriver_wait.until(
            EC.presence_of_element_located((By.XPATH,
            '//*[@id="tabContentBalance"]/div[2]/div/div/div[1]/table/tbody/tr[5]/td[2]/span'))
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
        return self._driver.find_element_by_id('ContentPlaceHolder1_MFALoginControl1_UserIDView_tbxPassword_UiInput')

    def _find_username_field(self):
        # hack
        employer_group = self._driver.find_element_by_xpath('//*[@id="ngb-panel-0-header"]/button')
        employer_group.click()
        sign_in_button = self._driver.find_element_by_xpath('//*[@id="ngb-panel-0"]/div/p/a')
        sign_in_button.click()
        sleep(1)
        return self._driver.find_element_by_id('ContentPlaceHolder1_MFALoginControl1_UserIDView_txtUserid_UiInput')

    @property
    def _login_url(self):
        return 'https://www.premera.com/portals/member/account/logon'

    def get_account_balance(self):
        self._login()
        #
        personal_funding_account = self._webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#cycCard > div > div > div > div.mb-0 > pbc-cta > a')))
        self._webdriver_wait.until(EC.visibility_of(personal_funding_account))
        sleep(1)
        personal_funding_account.click()
        sleep(1)
        # manage_your_account = self._webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#content-main > p:nth-child(5) > a')))
        # self._webdriver_wait.until(EC.visibility_of(manage_your_account))
        orig_tab = self._driver.window_handles[0]
        # manage_your_account.click()
        sleep(1)
        new_tab = None
        for tab in self._driver.window_handles:
            if tab != orig_tab:
                new_tab = tab

        if new_tab is None:
            raise Exception

        self._driver.switch_to_window(new_tab)
        self._webdriver_wait.until(text_has_loaded((By.ID, 'investmentBalance')))
        account_balance = self._driver.find_element_by_id('investmentBalance')
        return pennies_from_text(account_balance.text) + pennies_from_text("$2500.00")

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
        # This is ridiculous, but I don't know how else to get it to work.
        sleep(15)
        password = self._webdriver_wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        # password = self._webdriver_wait.until(EC.visibility_of(password))
        return password

    def _find_username_field(self):
        return self._webdriver_wait.until(EC.presence_of_element_located((By.ID, 'aw-personal-id')))

    def _login(self):
        self._driver.get(('https://onlinebanking.usbank.com/Auth/Login'))

        # fill in username and hit the next button
        username_field = self._find_username_field()
        username_field.send_keys(self._credentials.username)
        # username_field.send_keys(Keys.ENTER)

        try:
            # self._find_password_field()
            ActionChains(self._driver).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(self._credentials.password).send_keys(Keys.ENTER).perform()
            self._webdriver_wait.until(text_has_loaded((By.ID, 'DepositSpanHeaderTotal')))
        except TimeoutException:
            # Maybe timed out b/c there are security questions.
            security_box = self._webdriver_wait.until(
                EC.presence_of_element_located((By.ID, 'ans'))
               )
            question = self._driver.find_element_by_xpath('//*[@id="customUI"]/div[2]/form/label')
            security_box.send_keys(self._credentials.answer_security_question(question.text))
            security_box.send_keys(Keys.ENTER)
            sleep(5) # ew but I'm too scared to remove it.
            ActionChains(self._driver).send_keys(self._credentials.password).send_keys(Keys.ENTER).perform()


    def get_account_balance(self):
        self._login()
        self._webdriver_wait.until(text_has_loaded((By.ID, 'DepositSpanHeaderTotal')))
        account_balance = self._driver.find_element_by_id('DepositSpanHeaderTotal')
        return pennies_from_text(account_balance.text)