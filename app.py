from flask import Flask, g, make_response
import os
from werkzeug.utils import secure_filename
import models
from flask import request, jsonify
import uuid
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
import jwt
from celery import Celery
from functools import wraps
from utils.validate_request import validate_request
from sender.sender import sender
from utils.translators.translate_email_config_to_dict import translate_email_config_to_dict
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oidjsj092138u90fwej'

app.config.update(
    CELERY_BROKER_URL='amqp://user:password@broker:5672',
    CELERY_RESULT_BACKEND='amqp://user:password@broker:5672',
)

CORS(app)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'accessToken' in request.headers:
            token = request.headers['accessToken']

        if not token:
            return make_response('unauthorized', 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = models.User.get(public_id=data['public_id'])
        except:
            return make_response('token invalid', 401)

        return f(current_user, *args, **kwargs)

    return decorated


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/', methods=['GET'])
def index():
    return 'siemano'


@app.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.json

    hashed_password = generate_password_hash(data['password'])
    models.User.create_user(str(uuid.uuid4()), data['full_name'], data['email'], hashed_password)

    return jsonify({
        'message': 'New user created'
    })


@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return make_response(
        jsonify({
            'fullName': current_user.full_name,
            'email': current_user.email
        })
    )


@app.route('/auth', methods=['POST'])
def auth():
    data = request.json

    if 'email' not in data.keys() or 'password' not in data.keys():
        return make_response('Could not verify', 401)

    user = models.User.get(email=data['email'])

    if check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10),
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    else:
        return make_response('password incorrect', 401)


@app.route('/email-config', methods=['GET', 'POST'])
@token_required
def email_config(current_user):
    if request.method == 'GET':
        configs = models.EmailConfig.get_email_configs(current_user)
        parsed_configs = [{
            'configId': config.config_id,
            'email': config.email,
            'port': config.port,
            'ssl': config.ssl,
            'host': config.host
        } for config in configs]

        return make_response(jsonify({'configs': parsed_configs}), 200)

    if request.method == 'POST':
        data = request.json

        errors = validate_request(
            data,
            [
                'email',
                'ssl',
                'host',
                'port',
                'password'
            ]
        )

        if len(errors) >= 1:
            return make_response(str(errors), 400)

        models.EmailConfig.add_email_config(current_user, data)

        return make_response('new email config created', 201)


@app.route('/address-books', methods=['GET', 'POST'])
@token_required
def create_address_book(current_user):
    if request.method == 'GET':
        address_books_entries = models.AddressBook.get_address_books(current_user)
        address_books_parsed = [{
            'addressBookId': address_book.address_book_id,
            'name': address_book.name
        } for address_book in address_books_entries]

        return make_response(jsonify({'addressBooks': address_books_parsed}), 200)

    if request.method == 'POST':
        data = request.json

        errors = validate_request(data, ['name'])

        if len(errors) >= 1:
            return make_response(str(errors), 400)

        models.AddressBook.create_address_book(current_user, data['name'])

        return make_response('created address book', 201)


@app.route('/addresses/<int:address_book_id>', methods=['GET'])
@token_required
def get_addresses(current_user, address_book_id):
    addresses_entries = models.Address.get_addresses(address_book_id)
    addresses_parsed = [{
        'email': address.full_name,
        'fullName': address.full_name
    } for address in addresses_entries]

    return make_response(jsonify({'addresses': addresses_parsed}), 200)


@app.route('/addresses', methods=['POST'])
@token_required
def create_addresses(current_user):
    data = request.json

    errors = []

    if 'address-book' not in data:
        errors.append('address book is required')

    for address in data['addresses']:
        errors_from_single = validate_request(
            address,
            [
                'email',
                'full-name'
            ]
        )
        errors.extend(errors_from_single)

    if len(errors) >= 1:
        return make_response(str(errors), 400)

    for address in data['addresses']:
        models.Address.create_address(
            address['email'],
            address['full-name'],
            data['address-book']
        )

    return make_response('created addresses', 201)


@app.route('/images/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    image = request.files['image']
    if image:
        filename = secure_filename(image.filename)
        path = os.path.join('./uploads', filename)
        image.save(path)

        created_image = models.Image.add_image(current_user, path, filename)
        return make_response(jsonify({'image': created_image.image_id}), 201)


@app.route('/sessions/start', methods=['POST'])
@token_required
def start_session(current_user):
    # {
    #     image: 'image-id',
    #     email-config: 'config-id',
    #     subject: 'subject',
    #     address-book: 'address-book-id'
    # }

    send_emails.delay(request.json)

    return make_response(jsonify({}), 201)


@celery.task
def send_emails(data):
    session = models.Session.add_session()

    image_entry = models.Image.get(image_id=data['image'])
    image_path = image_entry.image_path

    with open(image_path, 'rb') as _image:
        image = _image.read()

    mail_config_entry = models.EmailConfig.get(config_id=data['email-config'])
    mail_config = translate_email_config_to_dict(mail_config_entry)

    sender.email_config(mail_config)
    sender.select_template()
    sender.create_connection()
    sender.set_image(image)

    def on_success(client_email):
        models.Event.add_event(
            session,
            mail_config_entry.email,
            client_email,
            'SUCCESS'
        )

    def on_failure(client_email):
        models.Event.add_event(
            session,
            mail_config_entry.email,
            client_email,
            'FAILURE'
        )

    sender.send_emails(
        data['subject'],
        models.AddressBook.get_addresses_from_book_for_sender(data['address-book']),
        on_success,
        on_failure
    )


@app.route('/sessions', methods=['GET'])
@token_required
def get_sessions(current_user):
    sessions_entries = models.Session.get_all_sessions()
    sessions_parsed = []

    for session in sessions_entries:
        events_entries = models.Event.get_events(session.session_id)
        successful_events_amount = len(
            [event for event in filter(
                lambda e: True if e.status == 'SUCCESS' else False,
                events_entries
            )]
        )
        failed_events_amount = len(
            [event for event in filter(
                lambda e: True if e.status == 'FAILURE' else False,
                events_entries
            )]
        )

        sessions_parsed = [
            *sessions_parsed,
            {
                'sessionId': session.session_id,
                'startedAt': session.startedAt,
                'successfulEvents': successful_events_amount,
                'failedEvents': failed_events_amount,
            }
        ]

    return make_response(jsonify({'sessions': sessions_parsed}), 200)


@app.route('/sessions/<int:session_id>', methods=['GET'])
@token_required
def get_events(current_user, session_id):
    events_entries = models.Event.get_events(session_id)
    events_parsed = [{
        'eventId': event.event_id,
        'emailFrom': event.email_from,
        'emailTo': event.email_to,
        'lastUpdate': event.last_update,
        'status': event.status
    } for event in events_entries]

    return make_response(jsonify({'events': events_parsed}), 200)


if __name__ == '__main__':
    app.run(DEBUG=True)
