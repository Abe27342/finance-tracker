
if __name__ == '__main__':
    import argparse
    from scrapers import USBankScraper, AllyScraper, FidelityScraper, VanguardScraper
    from datetime import datetime
    from credentials import get_vault
    from utils import get_driver, get_webdriver_wait

    parser = argparse.ArgumentParser(description = 'Read account balances and dump them to csv.')
    parser.add_argument('--output', type = str, help = 'Filepath to csv.')

    args = parser.parse_args()
    driver = get_driver()
    webdriver_wait = get_webdriver_wait(driver)
    vault = get_vault()
    website_scraper_pairs = [('usbank', USBankScraper), 
                             ('vanguard', VanguardScraper), 
                             ('ally', AllyScraper),
                             ('fidelity', FidelityScraper)]
    
    with open(args.output, 'a') as f:
        next_line = [str(datetime.now())]

        for website, scraper_class in website_scraper_pairs:
            print 'Gathering %s data.' % website
            scraper = scraper_class(driver, webdriver_wait, vault.get_website_credentials(website))
            try:
                account_balance = scraper.get_account_balance()
            except Exception:
                account_balance = 'N/A'

            next_line.append(account_balance)

        f.write(','.join([str(i) for i in next_line]) + '\n')

    driver.quit()