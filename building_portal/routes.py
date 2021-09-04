from pandas._libs.tslibs import NaT
from building_portal import app, sender_id, sender_password
from flask import redirect, render_template,flash, url_for, request
from building_portal.model import Dues, Flat, Maintenance, User, Events
from building_portal.forms import EndMaintenanceForm, RegisterForm, LoginForm, DuesForm, EventsForm, StartMaintenanceForm, EndMaintenanceForm
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
    admin_user = User.query.filter_by(admin_user = True).first()
    if admin_user and len(admin_user.name)>0:
        return render_template('home.html', admin_name = admin_user.name)
    else:
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
        if form.flat_no.data not in [number.flat_no for number in Flat.query.all()]:
            flat_to_create = Flat(flat_no=form.flat_no.data, floor=form.floor.data)
            flat_to_create.owner = User.query.filter_by(user_name=form.username.data).first().id
            db.session.add(flat_to_create)
            db.session.commit()
        else:
            flat_to_reassign = Flat.query.filter_by(id=form.flat_no.data).first()
            flat_to_reassign = User.query.filter_by(user_name=form.username.data).first().id
            db.session.commit()
        email_class = Email_Stakeholders()
        email_class.send_email(To_Addresses = form.email_address.data,
                                     Subject = "Creation of your account on Pushpa Kunj Residents Association Portal",
                                     Body=f"Hi {form.name.data}!\nWe're glad to welcome you to the Pushpa Kunj Family.\nWhile your registration has been received at our end, please wait for the current administrator to confirm your membership. You will only receive access to the full set of features after confirmation.",
                                     From_Address=sender_id,
                                     From_Password=sender_password)
        email_class.send_email(To_Addresses = User.query.filter_by(admin_user=True).first().email_address,
                                     Subject = f"A new user {form.name.data} of Flat number {form.flat_no.data} wishes to register",
                                     Body=f"A new user {form.name.data} has been created. You are requested to ratify his/her membership. On approving, he/she will gain access to the set of features available to all members",
                                     From_Address=sender_id,
                                     From_Password=sender_password)
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
def member_page():
    users = [user.id for user in User.query.all()]

    if request.method == "POST":
        for i in range(len(users)):
            data1 = request.form.get('admin')
            data2 = request.form.get('trash')
            
            if data1 == str(users[i]):
                user_to_change = User.query.filter_by(id=data1).first()
                user_to_change.admin_user = True
                current_user.admin_user = False
                email_class = Email_Stakeholders()
                email_class.send_email(To_Addresses = user_to_change.email_address,
                                     Subject = f"You have been made the new administrator of Pushpa Kunj by {current_user.name}",
                                     Body=f"Congratulations {user_to_change.name}!\nYou are now the new administrator of the Pushpa Kunj Residents Association",
                                     From_Address=sender_id,
                                     From_Password=sender_password)
                email_class.send_email(To_Addresses = current_user.email_address,
                                    Subject = f"You have transferred administrator privileges to {user_to_change.name}",
                                    Body=f"{user_to_change.name} has been made the new administrator of the Pushpa Kunj Residents Association on {datetime.now()}",
                                    From_Address=sender_id,
                                    From_Password=sender_password)
                db.session.commit()
            elif data2 == str(users[i]):
                user_to_change = User.query.filter_by(id=data2).delete()
                db.session.commit()
            else:
                pass

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
def employee_page():
    df = pd.read_csv('./Data/Employee_Data.csv')
    df = df[['Employee_Name','Designation']]
    return render_template('employees.html', employee_table = df)

@app.route('/assign_dues', methods=['GET','POST'])
def assign_dues_page():
    form=DuesForm()
    user_list = [(u.id, u.name) for u in User.query.all()]
    form.due_to_user.choices = user_list

    if form.validate_on_submit():
        due_to_create = Dues(amount = form.amount.data, purpose = form.purpose.data, status = False, created_on = datetime.now(), created_by = current_user.id, due_to_user = form.due_to_user.data)
        db.session.add(due_to_create)
        db.session.commit()
        email_class = Email_Stakeholders()
        email_class.send_email(To_Addresses = User.query.filter_by(id=form.due_to_user.data).first().email_address,
                                Subject = f"A new due of Rs{form.amount.data} has been raised against you",
                                Body=f"A new due of Rs{form.amount.data} has been raised against you by {current_user.name}.\nPurpose: {form.purpose.data}",
                                From_Address=sender_id,
                                From_Password=sender_password)
        return redirect(url_for('assign_dues_page'))
    
    dues = [due.id for due in Dues.query.all()]

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
def my_dues_page():
    try: 
        users = User.query.filter_by(id = current_user.id)
        dues = Dues.query.all(due_to_user = current_user.id)
        user_cols = ['id','name','email_address','contact_no','admin_user']
        dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']

        user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
        dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)
        dues_info = pd.merge(dues_df, user_df, left_on='Due_To_User', right_on='ID')
        dues_info = pd.merge(dues_info, user_df, left_on='Created_By', right_on='ID')
        dues_info = dues_info[['Amount','Purpose','Status','Created_On','Name_x','Name_y']]
        dues_info.columns = ['Amount','Purpose','Status','Created_On','Assignee','Assigner']
        dues_info = dues_info.sort_values(by=['Created_On'], ascending=False)
        return render_template('my_dues.html', dues_table = dues_info)
    except:
        return render_template('my_dues.html')

@app.route('/payment_history')
def payment_history_page():
    try:
        users = User.query.filter_by(id = current_user.id)
        dues = Dues.query.all(due_to_user = current_user.id)
        user_cols = ['id','name','email_address','contact_no','admin_user']
        dues_cols = ['id','amount','purpose','status','created_on','created_by','due_to_user']

        user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
        dues_df = db_to_dataframe(dues, ['ID','Amount','Purpose','Status','Created_On','Created_By','Due_To_User'], dues_cols)
        dues_info = pd.merge(dues_df, user_df, left_on='Due_To_User', right_on='ID')
        dues_info = pd.merge(dues_info, user_df, left_on='Created_By', right_on='ID')
        if dues_info.shape[0] > 1:
            dues_info = dues_info[dues_info['Status'] == True]
            dues_info = dues_info[['Amount','Purpose','Status','Created_On','Name_x','Name_y']]
            dues_info.columns = ['Amount','Purpose','Status','Created_On','Assignee','Assigner']
            dues_info = dues_info.sort_values(by=['Created_On'], ascending=False)
        return render_template('payment_history.html', dues_table = dues_info)
    except:
        return render_template('payment_history.html')

@app.route('/events', methods=['GET','POST'])
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
    
    events = [event.id for event in Events.query.all()]

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
def approve_members_page():
    users = [user.id for user in User.query.all()]

    if request.method == "POST":
        for i in range(len(users)):
            data1 = request.form.get('confirm')
            data2 = request.form.get('trash')
            
            if data1 == str(users[i]):
                user_to_change = User.query.filter_by(id=data1).first()
                user_to_change.confirmed = True
                user_to_change.confirmed_on = datetime.now()
                db.session.commit()
            elif data2 == str(users[i]):
                flat_to_remove = Flat.query.filter_by(owner=data2).delete()
                user_to_change = User.query.filter_by(id=data2).delete()
                db.session.commit()
            else:
                pass
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

@app.route('/maintenance_history', methods=['GET','POST'])
def maintenance_history_page():
    form=StartMaintenanceForm()
    form2=EndMaintenanceForm()
    if form.validate_on_submit():
        maintenance_to_create = Maintenance(title=form.title.data,
                                work_undertaken = form.work_undertaken.data,
                                estimated_cost = form.estimated_cost.data,
                                undertaken_on = form.undertaken_on.data,
                                estimated_completion_date = form.estimated_completion_date.data,
                                actual_cost = None,
                                actual_completion_date = None,
                                undertaken_by = current_user.id)

        db.session.add(maintenance_to_create)
        db.session.commit()
        return redirect(url_for('maintenance_history_page'))
    if form2.validate_on_submit():
        maintenance_to_change = Maintenance.query.filter_by(id = request.form.get('maintenance_id')).first()
        maintenance_to_change.actual_cost = form2.actual_cost.data
        maintenance_to_change.actual_completion_date = form2.actual_completion_date.data
        db.session.commit()
    users = User.query.all()
    maintenance = Maintenance.query.all()
    user_cols = ['id','name','email_address','contact_no','admin_user']
    maintenance_cols = ['id','title','work_undertaken','estimated_cost','undertaken_on','estimated_completion_date','actual_cost','actual_completion_date','undertaken_by']

    user_df = db_to_dataframe(users, ['ID','Name','Email_Address','Contact_Number', 'Administrator'], user_cols)
    maintenance_df = db_to_dataframe(maintenance, ['ID_main','Title','Work_Undertaken','Estimated_Cost','Undertaken_On','Estimated_Completion_Date','Actual_Cost','Actual_Completion_Date','Undertaken_By'], maintenance_cols)
    user_info = pd.merge(user_df, maintenance_df, left_on='ID', right_on='Undertaken_By')
    user_info['Undertaken_On'] = [datetime.strftime(date.date(), "%d %B %Y") for date in pd.to_datetime(user_info['Undertaken_On'])]
    user_info['Estimated_Completion_Date'] = [datetime.strftime(date.date(), "%d %B %Y") for date in pd.to_datetime(user_info['Estimated_Completion_Date'])]
    to_dates = []
    for date in user_info['Actual_Completion_Date']:
        if date!=None:
            # date = datetime(date)
            to_dates.append(datetime.strftime(date.date(), "%d %B %Y"))
        else:
            to_dates.append(None)
    user_info['Actual_Completion_Date'] = to_dates 
    return render_template('maintenance.html', form=form, form2 = form2, maintenance_table = user_info)