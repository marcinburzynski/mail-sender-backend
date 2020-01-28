import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "oidjsj092138u90fwej"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Development(Config):
    FLASK_ENV = 'development'
    DEBUG = True
