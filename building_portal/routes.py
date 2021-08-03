from building_portal import app
from flask import redirect, render_template,flash, url_for
from building_portal.model import Flat, User
from building_portal.forms import RegisterForm, LoginForm
from building_portal import db
from datetime import datetime
from flask_login import login_user
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

@app.route('/members')
def member_page():
    users = User.query.all()
    flats = Flat.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    flat_cols = ['flat_no','floor','owner']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    flat_df = db_to_dataframe(flats, ['Flat_Number','Floor','Owner'], flat_cols)
    user_info = pd.merge(user_df, flat_df, left_on='ID', right_on='Owner')
    user_info = user_info[['Name','Flat_Number','Floor', 'Contact_Number','Email_Address','Administrator']]
    # print(user_info)
    return render_template('members.html', member_table = user_info)

@app.route('/employees')
def employee_page():
    df = pd.read_csv('./Data/Employee_Data.csv')
    df = df[['Employee_Name','Designation']]
    return render_template('employees.html', employee_table = df)