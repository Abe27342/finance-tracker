from scrapers import *

website_scraper_pairs = [('usbank', USBankScraper),
                         ('vanguard', VanguardScraper),
                         ('ally', AllyScraper),
                         ('fidelity', FidelityScraper)]
                         # ('premera', PremeraScraper)]

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
    parser.add_argument('--debug', action = 'store_true', help = 'Don\'t catch errors or continue on failure.')
    parser.add_argument('--checkdate', action = 'store_true', help = 'Don\'t do any work if the log file has an entry from today already.')
    parser.add_argument('--profile', help = 'Profile to use for chromedriver; note that this is currently unused.')

    args = parser.parse_args()
    if args.checkdate:
        with open(args.output, 'r') as f:
            last_line = [line for line in f.readlines() if not line.isspace()][-1]
            current_time = datetime.now()
            # YYYY-MM-DD, so first 10 characters
            if str(current_time)[:10] == last_line[:10]:
                exit(0)

    driver = get_driver(args.debug, args.profile)
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
                if args.debug:
                    print(''.join(traceback.format_exc()))
                    # Don't quit--may want to look at page state.
                    # driver.quit()
                    exit(1)

                print(''.join(traceback.format_exc()))
                account_balance = 'N/A'
                if notifier:
                    try:
                        tb = ''.join(traceback.format_exc())
                        notifier.notify('An error occurred with the %s scraper.\n\n The traceback is shown below.\n\n %s' % (website, tb))
                    except Exception as eNotifier:
                        # Notifier went wrong...
                        pass

            next_line.append(account_balance)

        f.write(','.join([str(i) for i in next_line]) + '\n')

    driver.quit()