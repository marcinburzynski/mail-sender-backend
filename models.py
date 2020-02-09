from peewee import *
import datetime

DATABASE = PostgresqlDatabase('mailsender', user='mailadmin', password='Haslo123', host='db', port='5432')


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    public_id = CharField(unique=True)
    full_name = CharField(null=True)
    email = CharField(unique=True)
    password = CharField()

    @classmethod
    def create_user(cls, public_id, full_name, email, password):
        try:
            cls.create(
                public_id=public_id,
                full_name=full_name,
                email=email,
                password=password
            )
        except IntegrityError:
            raise ValueError('user already exists')


class Session(BaseModel):
    session_id = AutoField()
    startedAt = DateTimeField(default=datetime.datetime.utcnow())
    status = CharField(default='IN_PROGRESS')

    @classmethod
    def add_session(cls):
        session = cls.create()
        return session.session_id

    @classmethod
    def change_session_status(cls, session_id, status):
        session = cls.get(session_id=session_id)
        session.status = status
        session.save()

    @classmethod
    def get_all_sessions(cls):
        return cls.select()


class Event(BaseModel):
    event_id = AutoField()
    session = ForeignKeyField(Session)
    email_from = CharField()
    email_to = CharField()
    last_update = DateTimeField(default=datetime.datetime.utcnow())
    status = CharField(default='IN_PROGRESS')

    @classmethod
    def add_event(cls, session_id, email_from, email_to, status):
        session = Session.get(session_id=session_id)
        cls.create(
            session=session,
            email_from=email_from,
            email_to=email_to,
            status=status
        )

    @classmethod
    def update_event_state(cls, event_id, status):
        event = cls.get(event_id=event_id)
        event.status = status
        event.last_update = datetime.datetime.utcnow()
        event.save()

    @classmethod
    def get_events(cls, session_id):
        session = Session.select().where(Session.session_id == session_id)

        return cls.select().where(cls.session == session)


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

    @classmethod
    def get_email_configs(cls, current_user):
        return cls.select().where(cls.user == current_user)


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

    @classmethod
    def get_addresses_from_book_for_sender(cls, address_book_id):
        query = Address.select().where(Address.address_book == address_book_id)
        return [address.email for address in query]

    @classmethod
    def get_address_books(cls, current_user):
        return cls.select().where(cls.user == current_user)


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

    @classmethod
    def get_addresses(cls, address_book_id):
        address_book = AddressBook.select().where(AddressBook.address_book_id == address_book_id)
        return cls.select().where(cls.address_book == address_book)


class Image(BaseModel):
    image_id = AutoField()
    image_path = CharField(unique=True)
    image_name = CharField(null=True, unique=True)
    user = ForeignKeyField(User)

    @classmethod
    def add_image(cls, user, image_path, image_name=None):
        image = cls.create(
            user=user,
            image_path=image_path,
            image_name=image_name
        )

        return image
