from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import secrets

user_base = Flask(__name__)
user_base.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///website.db'
db = SQLAlchemy(user_base)  # database is being initialized
bcrypt = Bcrypt(user_base)
login_manager = LoginManager(user_base)
login_manager.login_view = 'login_form'
login_manager.login_message_category = 'info'

secret_key = secrets.token_hex(16)
user_base.config['SECRET_KEY'] = secret_key

from userbase import routes