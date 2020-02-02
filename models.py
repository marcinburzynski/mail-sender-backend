from peewee import *
import datetime

DATABASE = PostgresqlDatabase('mailsender', user='mailadmin', password='Haslo123', host='db', port='5432')


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    public_id = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    role = CharField()

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


class Session(BaseModel):
    session_id = AutoField()
    startedAt = DateTimeField(default=datetime.datetime.utcnow())
    status = CharField(default='IN_PROGRESS')

    @classmethod
    def add_session(cls):
        cls.create()

    @classmethod
    def change_session_status(cls, session_id, status):
        session = cls.get(session_id=session_id)
        session.status = status
        session.save()


class Event(BaseModel):
    event_id = AutoField()
    session = ForeignKeyField(Session)
    email_from = CharField()
    email_to = CharField()
    last_update = DateTimeField(default=datetime.datetime.utcnow())
    status = CharField(default='IN_PROGRESS')

    @classmethod
    def add_event(cls, session_id, email_from, email_to):
        session = Session.get(session_id=session_id)
        cls.create(
            session=session,
            email_from=email_from,
            email_to=email_to
        )

    @classmethod
    def update_event_state(cls, event_id, status):
        event = cls.get(event_id=event_id)
        event.status = status
        event.last_update = datetime.datetime.utcnow()
        event.save()


class EmailConfig(BaseModel):
    config_id = AutoField()
    email = CharField()
    password = CharField()
    port = IntegerField(null=True)
    ssl = BooleanField()
    host = CharField()
    user = ForeignKeyField(User)

    @classmethod
    def add_email_config(cls, user, config):

        cls.create(
            email=config['email'],
            password=config['password'],
            port=config['port'],
            ssl=config['ssl'],
            host=config['host'],
            user=user
        )


class AddressBook(BaseModel):
    user = ForeignKeyField(User)
    name = CharField()
    address_book_id = AutoField()

    @classmethod
    def create_address_book(cls, user, name):

        cls.create(
            user=user,
            name=name
        )


class Address(BaseModel):
    email = CharField()
    full_name = CharField(null=True)
    address_book = ForeignKeyField(AddressBook)

    @classmethod
    def create_address(cls, email, full_name, address_book_id):
        address_book = AddressBook.get(address_book_id=address_book_id)

        cls.create(
            email=email,
            full_name=full_name,
            address_book=address_book
        )
