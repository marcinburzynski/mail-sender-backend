from flask import Flask, g, make_response
import os
import models
from flask import request, jsonify
import uuid
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
import jwt
from celery import Celery
from functools import wraps
from utils.validate_request import validate_request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oidjsj092138u90fwej'

app.config.update(
    CELERY_BROKER_URL='amqp://user:password@broker:5672',
    CELERY_RESULT_BACKEND='amqp://user:password@broker:5672',
)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'access-token' in request.headers:
            token = request.headers['access-token']

        if not token:
            return make_response('unauthorized', 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = models.User.get(public_id=data['public_id'])
        except:
            return make_response('token invalid', 401)

        return f(current_user, *args, **kwargs)

    return decorated


@celery.task
def add(x, y):
    return x + y


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


@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json

    hashed_password = generate_password_hash(data['password'])
    models.User.create_user(str(uuid.uuid4()), data['email'], hashed_password, 'admin')

    return jsonify({
        'message': 'New user created'
    })


@app.route('/auth', methods=['POST'])
def auth():
    data = request.json

    if 'email' not in data.keys() or 'password' not in data.keys():
        return make_response('Could not verify', 401)

    user = models.User.get(email=data['email'])

    if check_password_hash(user.password, data['password']):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})
    else:
        return make_response('password incorrect')


@app.route('/create-email-config', methods=['POST'])
@token_required
def create_email_config(current_user):
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


@app.route('/create-address-book', methods=['POST'])
@token_required
def create_address_book(current_user):
    data = request.json

    errors = validate_request(data, ['name'])

    if len(errors) >= 1:
        return make_response(str(errors), 400)

    models.AddressBook.create_address_book(current_user, data['name'])

    return make_response('created address book', 201)


@app.route('/create-addresses', methods=['POST'])
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


@app.route('/start-session', methods=['POST'])
def start_session():
    data = request.json


if __name__ == '__main__':
    app.run(DEBUG=True)
