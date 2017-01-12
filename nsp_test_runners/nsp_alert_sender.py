class NSPAlertSender(object):

    def __init__(self, nsp_email_address, target_emails):
        self.nsp_email_address = nsp_email_address
        self.target_emails = target_emails

    def send_alert(self, alert_msg):
        pass
