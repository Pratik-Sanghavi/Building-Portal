from enum import unique
from building_portal import db, login_manager
from datetime import datetime
from building_portal import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30),nullable=False,unique=True)
    user_name = db.Column(db.String(length=30),nullable=False,unique=True)
    email_address = db.Column(db.String(length=50),nullable=False,unique=True)
    contact_no = db.Column(db.String(length=60),nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60),nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    admin_user = db.Column(db.Boolean(), nullable = False, unique = False, default=False)
    flat_no = db.relationship('Flat', backref='owned_user',lazy=True)
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)
    
    # def __init__(self,user_name=user_name, email_address=email_address, password_hash=password_hash, registered_on=datetime.now(), confirmed=False, confirmed_on=datetime.now(),  admin_user=False, flat_no=[]):
    #     self.user_name = user_name
    #     self.email_address = email_address
    #     self.password_hash = password_hash
    #     self.registered_on = registered_on
    #     self.confirmed = confirmed
    #     self.confirmed_on = confirmed_on
    #     self.admin_user = admin_user
    #     self.flat_no = flat_no

class Flat(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    flat_no = db.Column(db.Integer(), nullable=False, unique=True)
    floor = db.Column(db.Integer(), nullable=False)
    owner=db.Column(db.Integer(),db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Flat {self.name}'