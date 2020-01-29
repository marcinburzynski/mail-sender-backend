from smtplib import SMTP, SMTP_SSL


def create_connection(config):
    if config['ssl']:
        create_ssl_smtp_connection(config)
    else:
        create_smtp_connection(config)


def create_smtp_connection(config):
    try:
        smtp = SMTP(config['host'], config['port'])
        smtp.ehlo()
        smtp.login(config['username'], config['password'])
        return smtp
    except:
        print('Nie udało się połączyć z serwerem')


def create_ssl_smtp_connection(config):
    try:
        smtp = SMTP_SSL(config['host'], config['port'])
        smtp.ehlo()
        smtp.login(config['username'], config['password'])
        return smtp
    except:
        print('Nie udało się połączyć z serwerem')



