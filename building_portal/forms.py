from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, SelectField, DecimalField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, InputRequired
from building_portal.model import User,Flat
import phonenumbers

class RegisterForm(FlaskForm):
    # Naming below function in the given way is very important
    def validate_username(self, username_to_check):
        user = User.query.filter_by(user_name=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')
    
    def validate_flat_no(self, flat_no_to_check):
        flat_no = Flat.query.filter_by(flat_no=flat_no_to_check.data).first()
        if flat_no:
            raise ValidationError('User with Flat Number already exists! Please check with administrator')
    def validate_admin_user(self, admin_user_to_check):
        if admin_user_to_check.data == True:
            admin_exists = User.query.filter_by(admin_user=admin_user_to_check.data).first()
            if admin_exists:
                raise ValidationError(f'Administrator already exists! Please check with current administrator {admin_exists.user_name}')

    def validate_contact(self, phone_number_to_check):
        try:
            p = phonenumbers.parse(phone_number_to_check.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

    name = StringField(label='Full Name', validators=[Length(min=2, max=60),DataRequired()])
    username = StringField(label='User Name', validators=[Length(min=2, max=30),DataRequired()])
    contact_no = StringField(label='Contact Number', validators=[Length(min=10, max=10),DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(),DataRequired()])
    admin_user = BooleanField(label="Admin User (Check only if you are the building representative)")
    flat_no = IntegerField(label = "Flat Number", validators=[DataRequired()])
    floor = IntegerField(label = "Floor", validators=[DataRequired()])
    password1 = PasswordField(label = 'Password', validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label = 'Confirm Password', validators=[EqualTo('password1'),DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired()])
    password = PasswordField(label = 'Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class DuesForm(FlaskForm):
    amount = DecimalField(label='Amount', places=2, validators=[DataRequired()])
    purpose = StringField(label='Purpose', validators=[Length(min=2, max=100),DataRequired()])
    due_to_user = SelectField(label = "Assign to",coerce=int, validators=[InputRequired()])
    submit = SubmitField(label='Assign Payment')

class EventsForm(FlaskForm):
    title = StringField(label="Title", validators=[Length(min=2, max=200), DataRequired()])
    purpose = StringField(label="Purpose", validators=[Length(min=2, max=400), DataRequired()])
    submit = SubmitField(label='Create Event')