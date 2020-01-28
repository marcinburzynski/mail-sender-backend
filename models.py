from peewee import *

DATABASE = PostgresqlDatabase('mailsender', user='mailadmin', password='Haslo123', host='127.0.0.1', port='5432')


class User(Model):
    public_id = CharField()
    email = CharField(unique=True)
    password = CharField()
    role = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, public_id, email, password, role='USER'):
        try:
            cls.create(
                public_id=public_id,
                email=email,
                password=password,
                role=role
            )
        except IntegrityError:
            raise ValueError('user already exists')
