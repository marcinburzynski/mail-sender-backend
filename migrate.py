from os import system

system('pem init')
system('pem add models.User')
system('pem add models.Session')
system('pem add models.Event')
system('pem watch')
system('pem migrate')
