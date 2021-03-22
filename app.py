# app.py
# Authors: Chris Estes, Brian Carbonneau
from dataclasses import dataclass

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField, \
    PasswordField
from wtforms.validators import InputRequired, DataRequired, Length, Regexp, NumberRange
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://pf3n93rxwh14176k:zoat5w7a3vgn4rgl@ao9moanwus0rjiex.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/k98fz84q0v1bbm9t"
db = SQLAlchemy()
app.secret_key = 'topsecret'
db.init_app(app)
bootstrap = Bootstrap(app)
bcrypt = Bcrypt(app)
login = LoginManager(app)
login.login_view = 'login'


@dataclass
class Users(db.Model):
    user_id: int
    username: str
    password: str
    is_admin: str

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.String(1))

    def check_pw(self, checkstring):
        return bcrypt.check_password_hash(self.password, checkstring)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.user_id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')


@login.user_loader
def load_user(id):
    return Users.query.filter_by(user_id=id).first()


@dataclass
class Lists(db.Model):
    list_id: int
    user_id: int
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
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length")])
    password = StringField('Password', validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length")])
    is_admin = HiddenField()
    submit = SubmitField('Submit')


class CreateListForm(FlaskForm):
    list_name = StringField('List Name', validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length")])
    submit = SubmitField('Submit')


class CreateItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[InputRequired(), Length(min=3, max=20, message="Invalid Length")])
    item_description = StringField('Item Description',
                                   validators=[InputRequired(), Length(min=6, max=500, message="Invalid Length")])
    image_url = StringField('Image Url', validators=[InputRequired(), Length(min=6, max=200, message="Invalid Length")])
    item_url = StringField('Item Url', validators=[InputRequired(), Length(min=6, max=200, message="Invalid Length")])
    item_priority = IntegerField('Item Priority (1-10)', validators=[InputRequired()])
    submit = SubmitField('Submit')


class CreateLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


# root route
@app.route('/', methods=['GET'])
@login_required
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

        user = Users.query.filter_by(username=un).first()  # if this returns a user, then it already exists
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            message = f"Username taken, try Again."
            return render_template('createAccount.html', message=message)

        pw_hashed = bcrypt.generate_password_hash(pw).decode('utf-8')

        newuser = Users(username=un, password=pw_hashed, is_admin=ia)
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


# !!! not working, would work but needs to pull user_id from login session
@app.route('/createList', methods=['GET', 'POST'])
@login_required
def createList():
    listform = CreateListForm()
    if listform.validate_on_submit():
        ln = request.form['list_name']
        uid = current_user.user_id
        newlist = Lists(user_id=uid, list_name=ln)
        # Flask-SQLAlchemy adds to database here
        db.session.add(newlist)
        db.session.commit()
        # create a message to send to the template
        message = f"List was created."
        return render_template('createList.html', message=message)
    else:
        # show errors
        for field, errors in listform.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(listform, field).label.text,
                    error
                ), 'error')
        return render_template('createList.html', listform=listform)


# !!! not working needs to pull list_id from somewhere
@app.route('/createItem', methods=['GET', 'POST'])
@login_required
def createItem():
    itemform = CreateItemForm()
    if itemform.validate_on_submit():
        itemname = request.form['item_name']
        itemdesc = request.form['item_description']
        imgurl = request.form['image_url']
        itemurl = request.form['item_url']
        itempri = request.form['item_priority']
        # uid = (user_id) will have to fetch from persistent login later, add to "newitem" line later
        # lid = (list_id) will need to be passed in somehow, add to "newitem" line later
        newitem = Items(item_name=itemname, item_description=itemdesc, image_url=imgurl, item_url=itemurl,
                        item_priority=itempri)
        # Flask-SQLAlchemy adds to database here
        db.session.add(newitem)
        db.session.commit()
        # create a message to send to the template
        message = f"Item was created and added to list."
        return render_template('createItem.html', message=message)
    else:
        # show errors
        for field, errors in itemform.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(itemform, field).label.text,
                    error
                ), 'error')
        return render_template('createItem.html', itemform=itemform)


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
    # return jsonify({'item_id': 1, 'item_name': 'test item', 'item_description': 'test description',
    #                'item_url': 'https://www.youtube.com/watch?v=hzGmbwS_Drs', 'item_priority': 1,
    #                'list_id': 1, 'marked_user_id': 100})
    items = Items.query.all()
    return jsonify(items)


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
    lists = Lists.query.all()
    return jsonify(lists)


# Route for getting a specific list by list id from the DB
@app.route('/Lists:id=<id>', methods=['GET'])
def get_list_by_id(id):
    # we will return fake data until we have some lists present in the DB
    list = Lists.query.filter_by(list_id=id).first()
    return jsonify(list)


# Route for getting a list or lists from a specific user id from the DB
@app.route('/Lists:uid=<uid>', methods=['GET'])
def get_list_by_user_id(uid):
    # we will return fake data until we have some lists present in the DB
    # if user's only have one list:
    # list = List.query.filter_by(user_id=uid).first()
    # if user's have multiple lists:
    list = Lists.query.filter_by(user_id=uid).all()
    return jsonify(list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    loginform = CreateLoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    if loginform.validate_on_submit():
        user = Users.query.filter_by(username=loginform.username.data).first()
        if user is None or not user.check_pw(loginform.password.data):
            flash('Invalid username/password')
            return render_template('loginpage.html', title='Log In', loginform=loginform)
        login_user(user)
        return redirect(url_for('homepage'))
    return render_template('loginpage.html', title='Log In', loginform=loginform)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Currently for testing and demonstration, needs variable grab and connection to form?
@app.route('/updateList:lid=<lid>', methods=['GET'])
def updatelist(lid):
    list = Lists.query.filter_by(list_id=lid).one()
    if list:
        list.list_name = "test list edit 2"
        db.session.add(list)
        db.session.commit()
    lists = Lists.query.all()
    return jsonify(lists)


# Currently for testing and demonstration, needs variable grab and connection to button?
@app.route('/deleteList:lid=<lid>', methods=['GET'])
def deletelist(lid):
    list = Lists.query.filter_by(list_id=lid).one()
    if list:
        db.session.delete(list)
        db.session.commit()
    lists = Lists.query.all()
    return jsonify(lists)


# Currently for testing and demonstration, needs variable grab and connection to page form
@app.route('/updateItem:iid=<iid>', methods=['GET'])
def updateitem(iid):
    item = Items.query.filter_by(item_id=iid).one()
    if item:
        item.item_name = request.form['item_name']
        item.item_description = request.form['item_description']
        item.image_url = request.form['image_url']
        item.item_url = request.form['item_url']
        item.item_priority = request.form['item_priority']
        db.session.add(item)
        db.session.commit()
    items = Items.query.all()
    return jsonify(items)


# Currently for testing and demonstration, needs variable grab and connection to button?
@app.route('/deleteItem:iid=<iid>', methods=['GET'])
def deletelist(iid):
    item = Items.query.filter_by(item_id=iid).one()
    if item:
        db.session.delete(item)
        db.session.commit()
    items = Items.query.all()
    return jsonify(items)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
