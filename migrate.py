from os import system

system('pem init')
system('pem add models.User')
system('pem add models.Session')
system('pem add models.Event')
system('pem add models.EmailConfig')
system('pem add models.AddressBook')
system('pem add models.Address')
system('pem add models.Image')
system('pem watch')
system('pem migrate')
