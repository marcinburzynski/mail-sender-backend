from smtplib import SMTP, SMTP_SSL


def create_connection(config):
    if config['ssl']:
        return create_ssl_smtp_connection(config)
    else:
        return create_smtp_connection(config)


def create_smtp_connection(config):
    try:
        smtp = SMTP(config['host'], config['port'])
        smtp.ehlo()
        smtp.login(config['email'], config['password'])
        return smtp
    except:
        print('Nie udało się połączyć z serwerem')


def create_ssl_smtp_connection(config):
    try:
        smtp = SMTP_SSL(config['host'], config['port'])
        smtp.ehlo()
        smtp.login(config['email'], config['password'])
        return smtp
    except:
        print('Nie udało się połączyć z serwerem')



