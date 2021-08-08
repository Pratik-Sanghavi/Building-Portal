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
    dues_for_user = db.relationship('Dues', backref='dues_for_user',lazy=True)
    events_by_user = db.relationship('Events', backref='events_by_user',lazy=True)
    maintenance_by_user = db.relationship('Maintenance', backref='maintenance_by_user',lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash,attempted_password)

class Flat(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    flat_no = db.Column(db.Integer(), nullable=False, unique=True)
    floor = db.Column(db.Integer(), nullable=False)
    owner=db.Column(db.Integer(),db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Flat {self.name}'

class Dues(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amount = db.Column(db.Float(),nullable=False,unique=False)
    purpose = db.Column(db.String(length=100),nullable=False,unique=False)
    status = db.Column(db.Boolean(), nullable = False, unique = False, default=False)
    created_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)
    due_to_user = db.Column(db.Integer(),db.ForeignKey('user.id'))

class Events(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=200),nullable=False)
    purpose = db.Column(db.String(length=400),nullable=False)
    start_event = db.Column(db.DateTime, nullable=False, unique=True)
    end_event = db.Column(db.DateTime, nullable=False, unique=True)
    url = db.Column(db.String(length=100),nullable=False)
    created_by = db.Column(db.Integer(),db.ForeignKey('user.id'))

class Maintenance(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=150),nullable=False)
    work_undertaken = db.Column(db.String(length=700),nullable=False)
    estimated_cost = db.Column(db.Float(),nullable=False,unique=False)
    undertaken_by = db.Column(db.Integer(),db.ForeignKey('user.id'))