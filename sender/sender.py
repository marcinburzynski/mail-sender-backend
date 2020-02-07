import os

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

    def set_image(self, image):
        self.image = image

    def select_template(self):
        with open('./sender/templates/email.html') as template:
            self.template = template.read()

    def create_connection(self):
        self.connection = create_connection({
            'host': self.host,
            'port': self.port,
            'email': self.email,
            'password': self.password,
            'ssl': self.ssl
        })

    def send_emails(self, subject, mails, on_success, on_failure):
        for client_email in mails:
            try:
                constructed_email = construct_mail(
                    subject,
                    self.email,
                    client_email,
                    self.template,
                    self.image
                )
                self.connection.sendmail(
                    self.email,
                    client_email,
                    constructed_email
                )
                on_success(client_email)
            except:
                on_failure(client_email)


sender = Sender()
