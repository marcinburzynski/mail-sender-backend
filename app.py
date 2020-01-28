from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
import os
import models
from flask import request, jsonify
import json
import uuid
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))


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
    new_user = models.User.create_user(str(uuid.uuid4()), data['email'], hashed_password, 'admin')

    return jsonify({
        'message': 'New user created'
    })


if __name__ == '__main__':
    app.run(DEBUG=True)
