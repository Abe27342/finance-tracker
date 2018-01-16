import smtplib

class GmailNotifier:
    def __init__(self, credentials, destination_address):
        smtp_server = 'smtp.gmail.com:587'
        self.smtp_handler = smtplib.SMTP(smtp_server)
        self.credentials = credentials
        self.destination_address = destination_address

    def notify(self, message):
        """
        Used to send an email from the account specified with the credentials to the destination
        address.

        Args:
            message (str): Message body that should be sent
        Return: 
            (dict) Errors received from the smtp server
        """
        username = self.credentials.username
        password = self.credentials.password
        header = 'From: %s\n' % username
        header += 'To: %s\n' % self.destination_address
        header += 'Subject: Finance-tracker notification\n\n'
        message = header + message

        self.smtp_handler.starttls()
        self.smtp_handler.login(username, password)
        result = self.smtp_handler.sendmail(username, self.destination_address, message)
        self.smtp_handler.quit()
        return result
