from building_portal import app
from flask import redirect, render_template,flash, url_for
from building_portal.model import Flat, User
from building_portal.forms import RegisterForm, LoginForm
from building_portal import db
from datetime import datetime

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(user_name=form.username.data, email_address=form.email_address.data, password=form.password1.data, registered_on=datetime.now(), confirmed=False, confirmed_on=datetime.now(), admin_user = form.admin_user.data)
        db.session.add(user_to_create)
        db.session.commit()
        flat_to_create = Flat(flat_no=form.flat_no.data, floor=form.floor.data)
        flat_to_create.owner = User.query.filter_by(user_name=form.username.data).first().id
        db.session.add(flat_to_create)
        db.session.commit()
        return redirect(url_for('home'))
    if form.errors!={}: # if there are errors from validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
            
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form=LoginForm()
    return render_template('login.html', form=form)