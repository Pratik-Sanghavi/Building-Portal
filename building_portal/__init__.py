from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = "10b2a0072d1a65e325e76d75"
app.config['SESSION_COOKIE_NAME'] = "User"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///building.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()

sender_id = os.getenv('EMAIL_ID')
sender_password = os.getenv('PASSWORD')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from building_portal import routes