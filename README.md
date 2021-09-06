# Building-Portal
A portal for building tenants to view and track their payments, create events and reach out to other members and employees

## Requirements
1. Flask
   `pip install Flask`
2. Flask-SQLAlchemy
   `pip install Flask-SQLAlchemy`
3. Pandas
   `pip install pandas`
4. phonenumbers
   `pip install phonenumbers`
5. dotenv
   `pip install python-dotenv`
Let me know which ones I have missed here!

## Features
1. View members and employees' information
2. Assign and manage pending and paid dues
3. Create events (and send invites in the form of icalendar file over email) and view past and upcoming events
4. Create maintenance projects and close them<br>
Note: Create, update and delete operations are limited to the administrator<br>

## Features yet to be implemented
i. Voting in favour of a proposal (to be consulted with building members; Can be done with Google Forms or locally - whichever is preferable to members)<br>
ii. Responsive design of web application<br>
iii. Delete maintenance events<br>
iv. Personal Dashboard to view and modify personal information to be confirmed by the admin<br>
v. Creation of new employee to be added. Maybe add a table containing employee information in the model instead of the current method of a separate csv file.<br>
vi. Find a way to preserve user information whenever tenant of flat changes so as to look at data created for earlier user<br>
vii. Correct the .ics times to match the timezone (right now its pretty much random)

## Deploy on AWS EC2
To deploy on AWS EC2, follow this [link](https://levelup.gitconnected.com/how-to-deploy-a-flask-application-on-amazon-ec2-38837df3fa52)<br>
Note: Deploy using production not development server!! (Very important)
