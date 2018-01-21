from scrapers import *

website_scraper_pairs = [('usbank', USBankScraper), 
                         ('vanguard', VanguardScraper), 
                         ('ally', AllyScraper),
                         ('fidelity', FidelityScraper),
                         ('premera', PremeraScraper)]

if __name__ == '__main__':
    import traceback
    import argparse
    from datetime import datetime
    from credentials import get_vault
    from utils import *
    from notifiers import GmailNotifier

    parser = argparse.ArgumentParser(description = 'Read account balances and dump them to csv.')
    parser.add_argument('--output', type = str, help = 'Filepath to csv.')
    parser.add_argument('--email', type = str, help = 'Email address to send failure notifications to.')
    args = parser.parse_args()
    driver = get_driver()
    webdriver_wait = get_webdriver_wait(driver)
    vault = get_vault()

    if args.email:
        notifier = GmailNotifier(vault.get_website_credentials('gmail'), args.email)
    else:
        notifier = None

    with open(args.output, 'a') as f:
        next_line = [str(datetime.now())]
        for website, scraper_class in website_scraper_pairs:
            print 'Gathering %s data.' % website
            scraper = scraper_class(driver, webdriver_wait, vault.get_website_credentials(website))
            try:
                account_balance = scraper.get_account_balance()
            except Exception as e:
                account_balance = 'N/A'
                if notifier:
                    tb = ''.join(traceback.format_exc())
                    notifier.notify('An error occurred with the %s scraper.\n\n The traceback is shown below.\n\n %s' % (website, tb))

            next_line.append(account_balance)

        f.write(','.join([str(i) for i in next_line]) + '\n')

    driver.quit()
    exit(0)