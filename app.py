from flask import Flask, g, make_response
import os
import models
from flask import request, jsonify
import json
import uuid
from flask_bcrypt import generate_password_hash, check_password_hash
import datetime
import jwt
from celery import Celery

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oidjsj092138u90fwej'

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://user:password@broker:5672',
    CELERY_RESULT_BACKEND='amqp://user:password@broker:5672',
)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)

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
    data = json.loads(request.data.decode())

    hashed_password = generate_password_hash(data['password'])
    models.User.create_user(str(uuid.uuid4()), data['email'], hashed_password, 'admin')

    return jsonify({
        'message': 'New user created'
    })


@app.route('/auth', methods=['POST'])
def auth():
    data = json.loads(request.data.decode())

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


if __name__ == '__main__':
    app.run(DEBUG=True)
