import smtplib

class NSPAlertSender(object):

    def __init__(self, nsp_email_address, nsp_email_pwd, target_emails):
        self.nsp_email_address = nsp_email_address
        self.target_emails = target_emails
        self.nsp_email_pwd = nsp_email_pwd

    def send_alert(self, alert_msg):
        gmail_user = self.nsp_email_address
        gmail_pwd = self.nsp_email_pwd
        email_from = self.nsp_email_address
        email_to = self.target_emails
        subject = 'An NSP Alert'
        text = alert_msg

        # Prepare actual message
        message = '\From: {}\nTo: {}\nSubject: {}\n\n{}'.format(
            email_from, ", ".join(email_to), subject, text)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(email_from, email_to, message)
        server.close()
