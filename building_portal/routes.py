from building_portal import app, sender_id, sender_password
from flask import redirect, render_template,flash, url_for, request
from building_portal.model import Dues, Flat, User, Events
from building_portal.forms import RegisterForm, LoginForm, DuesForm, EventsForm
from building_portal import db
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from flask_security import login_required
import pandas as pd
from building_portal.load_functions import db_to_dataframe
from building_portal.email_class import Email_Stakeholders

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
                
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out successfully!", category='info')
    return redirect(url_for('home'))
    

@app.route('/members', methods=['GET','POST'])
@login_required
def member_page():
    users = [user.id for user in User.query.all()]

    if request.method == "POST":
        for i in range(len(users)):
            data1 = request.form.get('admin')
            
            if data1 == str(users[i]):
                user_to_change = User.query.filter_by(id=data1).first()
                user_to_change.admin_user = True
                current_user.admin_user = False
                db.session.commit()

    users = User.query.all()
    flats = Flat.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    flat_cols = ['flat_no','floor','owner']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    flat_df = db_to_dataframe(flats, ['Flat_Number','Floor','Owner'], flat_cols)
    user_info = pd.merge(user_df, flat_df, left_on='ID', right_on='Owner')
    
    user_info = user_info[['ID','Name','Flat_Number','Floor', 'Contact_Number','Email_Address','Administrator']]

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
        due_to_create = Dues(amount = form.amount.data, purpose = form.purpose.data, status = False, created_on = datetime.now(), created_by = current_user.id, due_to_user = form.due_to_user.data)
        db.session.add(due_to_create)
        db.session.commit()
        db.session.commit()
        return redirect(url_for('assign_dues_page'))
    # if form.errors!={}: # if there are errors from validations
        # for err_msg in form.errors.values():
            # flash(f'There was an error with creating a due: {err_msg}', category='danger')
    
    dues = [due.id for due in Dues.query.all()]
    # dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']
    # dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)

    if request.method == "POST":
        for i in range(len(dues)):
            data1 = request.form.get('check')
            data2 = request.form.get('trash')
            data3 = request.form.get('cross')
            
            if data1 == str(dues[i]):
                due_to_change = Dues.query.filter_by(id=data1).first()
                due_to_change.status = True
                db.session.commit()
            elif data2 == str(dues[i]):
                due_to_change = Dues.query.filter_by(id=data2).delete()
                db.session.commit()
            elif data3 == str(dues[i]):
                due_to_change = Dues.query.filter_by(id=data3).first()
                due_to_change.status = False
                db.session.commit()
            else:
                pass # unknown
    users = User.query.all()
    dues = Dues.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)
    dues_info = pd.merge(dues_df, user_df, left_on='Due_To_User', right_on='ID')
    dues_info = pd.merge(dues_info, user_df, left_on='Created_By', right_on='ID')
    dues_info = dues_info[['ID_x','Amount','Purpose','Status','Created_On','Name_x','Name_y']]
    dues_info.columns = ['ID','Amount','Purpose','Status','Created_On','Assignee','Assigner']
    dues_info = dues_info.sort_values(by=['Created_On'], ascending=False)
    return render_template('assign_dues.html', form=form, dues_table = dues_info)

@app.route('/my_dues')
@login_required
def my_dues_page():
    users = User.query.all()
    dues = Dues.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)
    dues_info = pd.merge(dues_df, user_df, left_on='Due_To_User', right_on='ID')
    dues_info = pd.merge(dues_info, user_df, left_on='Created_By', right_on='ID')
    dues_info = dues_info[dues_info['Due_To_User'] == current_user.id]
    dues_info = dues_info[['Amount','Purpose','Status','Created_On','Name_x','Name_y']]
    dues_info.columns = ['Amount','Purpose','Status','Created_On','Assignee','Assigner']
    dues_info = dues_info.sort_values(by=['Created_On'], ascending=False)
    return render_template('my_dues.html', dues_table = dues_info)

@app.route('/payment_history')
@login_required
def payment_history_page():
    users = User.query.all()
    dues = Dues.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)
    dues_info = pd.merge(dues_df, user_df, left_on='Due_To_User', right_on='ID')
    dues_info = pd.merge(dues_info, user_df, left_on='Created_By', right_on='ID')
    dues_info = dues_info[dues_info['Due_To_User'] == current_user.id]
    dues_info = dues_info[dues_info['Status'] == True]
    dues_info = dues_info[['Amount','Purpose','Status','Created_On','Name_x','Name_y']]
    dues_info.columns = ['Amount','Purpose','Status','Created_On','Assignee','Assigner']
    dues_info = dues_info.sort_values(by=['Created_On'], ascending=False)
    return render_template('payment_history.html', dues_table = dues_info)

@app.route('/events', methods=['GET','POST'])
@login_required
def events_page():
    form=EventsForm()
    if form.validate_on_submit():
        event_to_create = Events(title=form.title.data,
                                purpose = form.purpose.data,
                                start_event = datetime.combine(form.start_event_date.data, form.start_event_time.data),
                                end_event = datetime.combine(form.end_event_date.data, form.end_event_time.data),
                                url = form.url.data,
                                created_by = current_user.id)
        db.session.add(event_to_create)
        db.session.commit()
        email_class = Email_Stakeholders()
        email_class.send_email_with_invite(Date_Start = str(form.start_event_date.data),
                                           Time_Start = str(form.start_event_time.data),
                                           Date_End = str(form.end_event_date.data),
                                           Time_End = str(form.end_event_time.data),
                                           To_Addresses = [u.email_address for u in User.query.all()],
                                           Subject = form.title.data,
                                           Body = form.purpose.data,
                                           Url=form.url.data,
                                           From_Address = sender_id,
                                           From_Password = sender_password)
        return redirect(url_for('events_page'))
    # if form.errors!={}: # if there are errors from validations
        # for err_msg in form.errors.values():
            # flash(f'There was an error with creating a due: {err_msg}', category='danger')
    
    events = [event.id for event in Events.query.all()]
    # events_cols = ['id','title','purpose','start_event','end_event','url','created_by']
    # events_df = db_to_dataframe(events, ['ID','Title','Purpose','Start_Event','End_Event','URL','Created_By'], events_cols)

    if request.method == "POST":
        for i in range(len(events)):
            data1 = request.form.get('trash')
            
            if data1 == str(events[i]):
                event_to_change = Events.query.filter_by(id=data1).delete()
                db.session.commit()
            else:
                pass # unknown
    users = User.query.all()
    events = Events.query.all()
    
    user_cols = ['id','name','email_address','contact_no','admin_user']
    events_cols = ['id','title','purpose','start_event','end_event','url','created_by']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    events_df = db_to_dataframe(events, ['ID','Title','Purpose','Start_Event','End_Event','URL','Created_By'], events_cols)
    events_info = pd.merge(events_df, user_df, left_on='Created_By', right_on='ID')
    events_info = events_info.sort_values(by=['Start_Event'], ascending=False)
    events_info = events_info[['ID_x','Title','Purpose','Start_Event','End_Event','URL','Created_By','Name']]
    return render_template('events.html', form=form, events_table = events_info)

@app.route('/approve_members', methods=['GET','POST'])
@login_required
def approve_members_page():
    users = [user.id for user in User.query.all()]

    if request.method == "POST":
        for i in range(len(users)):
            data1 = request.form.get('confirm')
            
            if data1 == str(users[i]):
                user_to_change = User.query.filter_by(id=data1).first()
                user_to_change.confirmed = True
                user_to_change.confirmed_on = datetime.now()
                db.session.commit()
    users = User.query.all()
    flats = Flat.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user','confirmed']
    flat_cols = ['flat_no','floor','owner']
    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator','Confirmed'], user_cols)
    flat_df = db_to_dataframe(flats, ['Flat_Number','Floor','Owner'], flat_cols)
    user_info = pd.merge(user_df, flat_df, left_on='ID', right_on='Owner')
    user_info = user_info[user_info['Confirmed']==False]
    user_info = user_info[['ID','Name','Flat_Number','Floor', 'Contact_Number','Email_Address','Administrator']]

    return render_template('approve_members.html', member_table = user_info)
