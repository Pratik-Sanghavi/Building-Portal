import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from ics import Calendar, Event
import os

class Email_Stakeholders():
    def send_email_with_invite(self, Date_Start, Time_Start, Date_End, Time_End, To_Addresses, Subject, Body, Url, From_Address, From_Password):
        c = Calendar()
        e = Event()
        e.name = Subject
        e.description = str(Body) + "\nMeeting Link:\n" + str(Url)
        e.begin = str(Date_Start) + str(Time_Start)
        e.end = str(Date_End) + str(Time_End)
        e.url = str(Url)
        c.events.add(e)
        if not os.path.exists('./Invite'):
            os.makedirs('./Invite')
        with open('./Invite/invite.ics', 'w') as f:
            f.write(str(c))
        # instance of MIMEMultipart
        msg = MIMEMultipart()

        # storing the senders email address
        msg['From'] = From_Address

        # storing the receivers email address
        msg['To'] = ", ".join(To_Addresses)

        # storing the subject
        msg['Subject'] = Subject

        # string to store the body of the mail
        body = str(Body) + "\nMeeting Link:\n" + str(Url) + "\nThis is a system generated email.\nPlease do not reply to this email"

        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # open the file to be sent
        filename = './Invite/invite.ics'
        attachment = open(f"{filename}", "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)

        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(From_Address, From_Password)

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(From_Address, To_Addresses, text)

        # terminating the session
        s.quit()

    def send_email(self, To_Addresses, Subject, Body, From_Address, From_Password):
        # instance of MIMEMultipart
        msg = MIMEMultipart()

        # storing the senders email address
        msg['From'] = From_Address

        # storing the receivers email address
        msg['To'] = ", ".join(To_Addresses)

        # storing the subject
        msg['Subject'] = Subject

        # string to store the body of the mail
        body = str(Body) + "\nThis is a system generated email.\nPlease do not reply to this email"

        # attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(From_Address, From_Password)

        # Converts the Multipart msg into a string
        text = msg.as_string()

        # sending the mail
        s.sendmail(From_Address, To_Addresses, text)

        # terminating the session
        s.quit()