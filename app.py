# app.py
# Authors: Chris Estes
from dataclasses import dataclass

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://pf3n93rxwh14176k:zoat5w7a3vgn4rgl@ao9moanwus0rjiex.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/k98fz84q0v1bbm9t"
db = SQLAlchemy()
app.secret_key = 'topsecret'
db.init_app(app)
Bootstrap(app)


@dataclass
class Users(db.Model):
    user_id: int
    username: str
    password: str
    is_admin: str

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    is_admin = db.Column(db.String(1))


@dataclass
class Lists(db.Model):
    list_id: int
    user_id: str
    list_name: str

    list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # foreign key is from users table
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # define relationship between lists and users

    users = db.relationship('Users', backref=db.backref('lists', lazy=True))
    list_name = db.Column(db.String(20))


@dataclass
class Items(db.Model):
    item_id: int
    item_name: str
    item_description: str
    image_url: str
    item_url: str
    item_priority: int
    list_id: int
    marked_user_id: int

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(20))
    item_description = db.Column(db.String(500))
    image_url = db.Column(db.String(200))
    item_url = db.Column(db.String(200))
    item_priority = db.Column(db.String(2))

    # foreign key is from Lists table
    list_id = db.Column(db.Integer, db.ForeignKey('lists.list_id'))
    # define relationship between items and lists
    lists = db.relationship('Lists', backref=db.backref('items', lazy=True))

    # foreign key is from Users table
    marked_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # define relationship between items and users
    users = db.relationship('Users', backref=db.backref('items', lazy=True))


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=6, max=20, message="Invalid Length")])
    password = StringField('Password', validators=[InputRequired(),Length(min=6, max=20, message="Invalid Length")])
    is_admin = HiddenField()
    submit = SubmitField('Submit')


# root route
@app.route('/', methods=['GET', 'POST'])
def loginpage():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'test' or request.form['password'] != 'test':
            error = 'Invalid Credentials. Try again or Create Account.'
        else:

            return redirect(url_for('homepage'))
    return render_template('loginpage.html', error=error)


@app.route('/homepage')
def homepage():
    return render_template("homepage.html")

# currently testing and trying to make work
@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    userform = CreateUserForm()
    if userform.validate_on_submit():
        un = request.form['username']
        pw = request.form['password']
        ia = 'N'
        newuser = Users(username=un, password=pw, is_admin=ia)
        # Flask-SQLAlchemy adds to database here
        db.session.add(newuser)
        db.session.commit()
        # create a message to send to the template
        message = f"User was created."
        return render_template('createAccount.html', message=message)
    else:
        # show errors
        for field, errors in userform.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(userform, field).label.text,
                    error
                ), 'error')
        return render_template('createAccount.html', userform=userform)


@app.route('/logout')
def logout():
    return redirect(url_for('loginpage'))


# example template
@app.route('/template-test')
def test():
    return render_template("test.html")


# example json return
@app.route('/json-test')
def returnJson():
    return jsonify({'test': 'var'})

# Users Endpoints
# Route for getting a list of all users from DB
@app.route('/Users')
def getUsers():
    users = Users.query.all()
    return jsonify(users)

# Route for getting a single user based on their ID from DB
@app.route('/Users:id=<id>', methods=['GET'])
def get_user_by_id(id):
    user = Users.query.filter_by(user_id=id).first()
    return jsonify(user)

# Route for getting a single user based on their username from DB
@app.route('/Users:n=<username>', methods=['GET'])
def get_user_by_username(username):
    user = Users.query.filter_by(username=username).first();
    return jsonify(user)

# Route for getting only the username based on their ID from DB
@app.route('/Users:id=<id>/username', methods=['GET'])
def get_username_by_id(id):
    user = Users.query.filter_by(user_id=id).first()
    return jsonify(user.username)

# Items Endpoints
# Route for getting a list of all items from the DB
@app.route('/Items', methods=['GET'])
def getItems():
    # we will return fake data until we have some items present in the DB
    return jsonify({'item_id': 1, 'item_name': 'test item', 'item_description': 'test description',
                    'item_url': 'https://www.youtube.com/watch?v=hzGmbwS_Drs', 'item_priority': 1,
                    'list_id': 1, 'marked_user_id': 100})

# Route for getting a list of all items for a specific list id from the DB
@app.route('/Items:lid=<lid>', methods=['GET'])
def get_items_by_list_id(lid):
    # we will return fake data until we have some items present in the DB
    return jsonify({'item_id': 1, 'item_name': 'test item', 'item_description': 'test description',
                    'item_url': 'https://www.youtube.com/watch?v=0DHrgwLxbGU', 'item_priority': 1,
                    'list_id': lid, 'marked_user_id': 100})

# Lists Endpoints
# Route for getting a list of all lists from the DB
@app.route('/Lists', methods=['GET'])
def getLists():
    # we will return fake data until we have some lists present in the DB
    # lists = Lists.query.all()
    # return jsonify(lists)
    return jsonify({'list_id': 1, 'user_id': 1, 'list_name': 'test list'})

# Route for getting a specific list by list id from the DB
@app.route('/Lists:id=<id>', methods=['GET'])
def get_list_by_id(id):
    # we will return fake data until we have some lists present in the DB
    # list = Lists.query.filter_by(list_id=id).first()
    # return jsonify(list)
    return jsonify({'list_id': id, 'user_id': 1, 'list_name': 'test list'})

# Route for getting a list or lists from a specific user id from the DB
@app.route('/Lists:uid=<uid>', methods=['GET'])
def get_list_by_user_id(uid):
    # we will return fake data until we have some lists present in the DB
    # if user's only have one list:
    # list = List.query.filter_by(user_id=uid).first()
    # if user's have multiple lists:
    # list = list.query.filter_by(user_id=uid).all()
    # return jsonify(list)
    return jsonify({'list_id': 1, 'user_id': uid, 'list_name': 'test list'})


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
