from scrapers import USBankScraper, AllyScraper, FidelityScraper, VanguardScraper
from datetime import datetime
from credentials import get_vault

if __name__ == '__main__':
    from utils import get_driver, get_webdriver_wait
    from credentials import JSONCredentials

    driver = get_driver()
    webdriver_wait = get_webdriver_wait(driver)
    vault = get_vault()

    website_scraper_pairs = [('usbank', USBankScraper), 
                             ('vanguard', VanguardScraper), 
                             ('ally', AllyScraper),
                             ('fidelity', FidelityScraper)]

    with open('C:/Users/Abram/OneDrive - Harvey Mudd College/Finance/net_worth.csv', 'a') as f:
        next_line = [str(datetime.now())]

        for website, scraper_class in website_scraper_pairs:
            print 'Gathering %s data.' % website
            scraper = scraper_class(driver, webdriver_wait, vault.get_website_credentials(website))
            next_line.append(scraper.get_account_balance())

        f.write(','.join([str(i) for i in next_line]) + '\n')

    driver.quit()
