from peewee import *
import datetime

DATABASE = PostgresqlDatabase('mailsender', user='mailadmin', password='Haslo123', host='127.0.0.1', port='5432')


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(BaseModel):
    public_id = CharField()
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



