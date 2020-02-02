from .connector import create_connection
from .mail_constructor import construct_mail


class Sender:
    def __init__(self):
        self.host = None
        self.template = None
        self.image = None
        self.email = None
        self.ssl = None
        self.port = None
        self.password = None
        self.connection = None

    def email_config(self, config):
        self.host = config['host']
        self.email = config['email']
        self.ssl = config['ssl']
        self.port = config['port']
        self.password = config['password']

    def select_template(self):
        with open('./templates/email.html') as template:
            self.template = template

    def create_connection(self):
        self.connection = create_connection({
            'host': self.host,
            'port': self.port,
            'email': self.email,
            'password': self.password,
            'ssl': self.ssl
        })

    def send_emails(self, subject, mails, on_success, on_fail):
        for clientEmail in mails:
            try:
                constructed_email = construct_mail(
                    subject,
                    self.email,
                    clientEmail,
                    self.template,
                    self.image
                )
                self.connection.sendmail(
                    self.email,
                    clientEmail,
                    constructed_email
                )
                on_success()
            except:
                on_fail()


sender = Sender()
