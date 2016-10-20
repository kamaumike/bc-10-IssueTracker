from flask import Flask, request, flash, url_for, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
#from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///issues.db'
app.config['SECRET_KEY'] = "mysecret"
login_manager = LoginManager(app)

db = SQLAlchemy(app)

class Users(db.Model):
    """Create the users table"""

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False, nullable=False)
    last_name = db.Column(db.String(64), index=True, unique=False)    
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64), index=True, unique=False)
    is_admin = db.Column(db.Boolean, index=True, unique=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    #initializing the users model
    def __init__(self, first_name, last_name, email, password, department_id, is_admin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.department_id = department_id
	
    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

class Departments(db.Model):
    """Create the departments table"""
    id = db.Column(db.Integer, primary_key = True, nullable=False)
    name = db.Column(db.String(64), index=True, unique=True)
     
    #initializing the department model 
    def __init__(self, name):
        self.name = name
           

class Issues(db.Model):
    """Create the issues table"""
    id = db.Column(db.Integer, primary_key = True)
    issue_description = db.Column(db.String(180))
    priority = db.Column(db.String(10), index=True, unique=False)
    status = db.Column(db.String(10), index=True,unique=False)
    timestamp = db.Column(db.DateTime)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
          
    #initializing the issues model
    def __init__(self, issue_description, priority,department_id):
        self.issue_description = issue_description
        self.priority = priority
        self.status = "open"
        self.timestamp = datetime.now()
        self.department_id = department_id
        
#home page
@app.route('/')
def index():
   return render_template('index.html')

#register user
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
   departments = Departments.query.all()
   if request.method == 'POST':
      if not request.form['first_name'] or not request.form['last_name'] or not request.form['email'] or not request.form['password'] or not request.form['department_id']:
        flash('Please enter all the fields', 'error')
      else:
        user = Users(request.form['first_name'], request.form['last_name'], request.form['email'], request.form['password'], request.form['department_id'])
        db.session.add(user)
        try:
            db.session.commit()
            flash('Record was successfully added')
        except Exception as e:
            flash('Error Occured!')
            flash(e)
        return redirect(url_for('login'))
   return render_template('signup.html', departments = departments)

#login page
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email']
    password = request.form['password']
    registered_user = Users.query.filter_by(email=email,password=password).first()
    
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(url_for('add_issue'))

#logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#register department
@app.route('/department/add', methods = ['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        if not request.form['name']:
            flash('This field is required!', 'error')
        else:
            department= Departments(request.form['name'])        
            db.session.add(department)
            try:
                db.session.commit()
                flash('Record was successfully added')
            except Exception as e:
                flash('Error Occured!')
                flash(e)
            return redirect(url_for('add_department'))
    return render_template('add_department.html')



#add an issue
@app.route('/issue/add', methods = ['GET', 'POST'])
def add_issue():
   departments = Departments.query.all()
   if request.method == 'POST':
      if not request.form['issue_description'] or not request.form['priority'] or not request.form['department_id']:
        flash('Please enter all the fields', 'error')
      else:
        issue = Issues(request.form['issue_description'], request.form['priority'], request.form['department_id'])        
        db.session.add(issue)
        try:
            db.session.commit()
            flash('Record was successfully added')
        except Exception as e:
            # db.session.rollback()
            flash('Error Occured!')
            flash(e)
        return redirect(url_for('index'))
   return render_template('add_issue.html', departments = departments)


@login_manager.user_loader
def load_user(user_id):
     """Returns a user object"""
     return Users.query.get(user_id)

# Start development web server
if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)