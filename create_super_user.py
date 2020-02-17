from flask_bcrypt import generate_password_hash
import models
import uuid

password = input('password\n> ')
username = input('username\n> ')
hashed_password = generate_password_hash(password)
models.User.create_user(str(uuid.uuid4()), 'Super User', username, hashed_password)
