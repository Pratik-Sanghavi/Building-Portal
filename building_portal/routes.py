from building_portal import app, sender_id, sender_password
from flask import redirect, render_template,flash, url_for
from building_portal.model import Dues, Flat, User
from building_portal.forms import RegisterForm, LoginForm, DuesForm
from building_portal import db
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from flask_security import login_required
import pandas as pd
from building_portal.load_functions import db_to_dataframe

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(name=form.name.data,
                              user_name=form.username.data,
                              email_address=form.email_address.data, 
                              contact_no=form.contact_no.data,
                              password=form.password1.data, 
                              registered_on=datetime.now(), 
                              confirmed=False, 
                              confirmed_on=datetime.now(), 
                              admin_user = form.admin_user.data)
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
    if form.validate_on_submit():
        attempted_user  = User.query.filter_by(user_name=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as {attempted_user.user_name}', category='success')
            return redirect(url_for('home'))
        else:
            flash('Username and password do not match! Please check your login credentials or contact admin.', category='danger')
            pass    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out successfully!", category='info')
    return redirect(url_for('home'))
    

@app.route('/members')
@login_required
def member_page():
    users = User.query.all()
    flats = Flat.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    flat_cols = ['flat_no','floor','owner']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    flat_df = db_to_dataframe(flats, ['Flat_Number','Floor','Owner'], flat_cols)
    user_info = pd.merge(user_df, flat_df, left_on='ID', right_on='Owner')
    user_info = user_info[['Name','Flat_Number','Floor', 'Contact_Number','Email_Address','Administrator']]
    return render_template('members.html', member_table = user_info)

@app.route('/employees')
@login_required
def employee_page():
    df = pd.read_csv('./Data/Employee_Data.csv')
    df = df[['Employee_Name','Designation']]
    return render_template('employees.html', employee_table = df)

@app.route('/assign_dues', methods=['GET','POST'])
@login_required
def assign_dues_page():
    form=DuesForm()
    user_list = [(u.id, u.name) for u in User.query.all()]
    form.due_to_user.choices = user_list
    if form.validate_on_submit():
        print("Okay")
        due_to_create = Dues(amount = form.amount.data, purpose = form.purpose.data, status = False, created_on = datetime.now(), created_by = current_user.id, due_to_user = form.due_to_user.data)
        db.session.add(due_to_create)
        db.session.commit()
        db.session.commit()
        return redirect(url_for('assign_dues_page'))
    else:
        print(f"Errors: {form.errors}")
    if form.errors!={}: # if there are errors from validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a due: {err_msg}', category='danger')
            print(f'There was an error with creating a due: {err_msg}')
    return render_template('assign_dues.html', form=form)

@app.route('/events')
@login_required
def events_page():
    form=DuesForm()
    return render_template('events.html', form=form)