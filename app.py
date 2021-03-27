# app.py
# Authors: Chris Estes, Brian Carbonneau, Madeleine Macaulay, Breanna Holloman
from dataclasses import dataclass

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
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
    is_admin: chr

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.CHAR(1))

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

    users = db.relationship('Users', backref=db.backref('lists', cascade="all, delete-orphan", lazy=True))
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
    lists = db.relationship('Lists', backref=db.backref('items', cascade="all, delete-orphan", lazy=True))

    # foreign key is from Users table
    marked_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # define relationship between items and users
    users = db.relationship('Users', backref=db.backref('items', lazy=True))


@dataclass
class Friends(db.Model):
    fusername: str
    link_id: int
    friend_id: int
    user_id: int

    link_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fusername = db.Column(db.String(20))

    # foreign key is from users table
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # define relationship between lists and users

    user = db.relationship('Users', foreign_keys=[user_id],
                           backref=db.backref('friends', cascade="all, delete-orphan", lazy=True))
    friend = db.relationship('Users', foreign_keys=[friend_id],
                             backref=db.backref('friends2', cascade="all, delete-orphan", lazy=True))


class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length")])
    # regex based on: https://www.geeksforgeeks.org/check-if-a-string-contains-uppercase-lowercase-special-characters-and-numeric-values/
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length"),
                                                     Regexp(regex="(?=.*[a-zA-Z])(?=.*\\d)(?=.*[-+_!@#$%^&*., ?])+",
                                                            message="Must be alphanumeric AND contain a special character")])
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
    submit = SubmitField('Sign-In')


class CreateUsernameSettingsForm(FlaskForm):
    desiredUsername = StringField('Desired Username', validators=[InputRequired()])
    submit = SubmitField('Update Username')


class CreatePasswordSettingsForm(FlaskForm):
    currentPassword = PasswordField('Current Password', validators=[InputRequired()])
    # regex based on: https://www.geeksforgeeks.org/check-if-a-string-contains-uppercase-lowercase-special-characters-and-numeric-values/
    newPassword = PasswordField('New Password',
                                validators=[InputRequired(), Length(min=6, max=500, message="Invalid Length"),
                                            Regexp(regex="(?=.*[a-zA-Z])(?=.*\\d)(?=.*[-+_!@#$%^&*., ?])+",
                                                   message="Must be alphanumeric AND contain a special character")])
    submit = SubmitField('Update Password')


class CreateFriendForm(FlaskForm):
    fusername = StringField('Friends Username',
                            validators=[InputRequired(), Length(min=6, max=20, message="Invalid Length")])
    submit = SubmitField('Add Friend')


@app.context_processor
def checkAdmin():
    if (session.get('is_admin', None) == 'Y'):
        return dict(isAdmin='true')
    else:
        return dict(isAdmin='false')


# root route
@app.route('/', methods=['GET'])
@login_required
def homepage():
    user_id = session.get('user_id', None)
    return render_template("homepage.html", id=user_id)


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


@app.route('/createList', methods=['GET', 'POST'])
@login_required
def createList():
    listform = CreateListForm()
    if listform.validate_on_submit():
        ln = request.form['list_name']
        uid = session.get('user_id', None)
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
        uid = session.get('user_id', None)
        lid = session.get('list_id', None)
        newitem = Items(item_name=itemname, item_description=itemdesc, image_url=imgurl, item_url=itemurl,
                        item_priority=itempri, list_id=lid)
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


# user settings route
@app.route('/userSettings', methods=['GET', 'POST'])
@login_required
def userSettings():
    user_id = session.get('user_id', None)
    return render_template('userSettings.html', user_id=user_id)


# edit username
@app.route('/userSettings/editUsername', methods=['GET', 'POST'])
@login_required
def editUsername():
    user_id = session.get('user_id', None)
    settingsForm = CreateUsernameSettingsForm()
    if settingsForm.validate_on_submit():
        dun = request.form['desiredUsername']
        print("Desired name: " + dun);
        user = Users.query.filter_by(username=dun).first()  # if this returns a user, then it already exists
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            message = f"Username taken, try Again."
            return render_template('editUsername.html', user_id=user_id, message=message,
                                   usernameSettingsForm=settingsForm)
        if not user:
            user = Users.query.filter_by(user_id=user_id).first()
            if user.user_id == user_id:
                user.username = dun
                db.session.commit()

    return render_template('editUsername.html', user_id=user_id, usernameSettingsForm=settingsForm)


# edit password
@app.route('/userSettings/editPassword', methods=['GET', 'POST'])
@login_required
def editPassword():
    user_id = session.get('user_id', None)
    settingsForm = CreatePasswordSettingsForm()
    if settingsForm.validate_on_submit():
        cpw = request.form['currentPassword']
        npw = request.form['newPassword']
        print("New password passes regex: " + npw)
        user = Users.query.filter_by(user_id=user_id).first()  # if this returns a user, then it already exists
        if user is None or not user.check_pw(cpw):
            message = f"Incorrect Password."
            return render_template('editPassword.html', user_id=user_id, passwordSettingsForm=settingsForm,
                                   message=message)
        if user and user.check_pw(cpw) and (user_id == user.user_id or session.get('is_admin', None) == 'Y'):
            pw_hashed = bcrypt.generate_password_hash(npw).decode('utf-8')
            user.password = pw_hashed
            db.session.commit()

    return render_template('editPassword.html', user_id=user_id, passwordSettingsForm=settingsForm)


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
    items = Items.query.all()
    return jsonify(items)


# Route for getting a list of all items for a specific list id from the DB
@app.route('/Items:lid=<lid>', methods=['GET'])
def get_items_by_list_id(lid):
    items = Items.query.filter_by(list_id=lid).all()
    return jsonify(items)


# Lists Endpoints
# Route for getting a list of all lists from the DB
@app.route('/Lists', methods=['GET'])
def getLists():
    lists = Lists.query.all()
    return jsonify(lists)


# Route for getting a specific list by list id from the DB
@app.route('/Lists:id=<id>', methods=['GET'])
def get_list_by_id(id):
    list = Lists.query.filter_by(list_id=id).first()
    return jsonify(list)


# Route for getting a list or lists from a specific user id from the DB
@app.route('/Lists:uid=<uid>', methods=['GET'])
def get_list_by_user_id(uid):
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
        session['user_id'] = user.user_id
        session['is_admin'] = user.is_admin
        return redirect(url_for('homepage'))
    return render_template('loginpage.html', title='Log In', loginform=loginform)


@app.route('/adminSettings')
@login_required
def adminSettings():
    if (session.get('is_admin', None) != 'Y'):
        return render_template('homepage.html')
    else:
        return render_template('adminSettings.html')


@app.route('/adminListSettings')
@login_required
def adminListSettings():
    if (session.get('is_admin', None) != 'Y'):
        return render_template('homepage.html')
    else:
        return render_template('adminListSettings.html')


@app.route('/adminUserSettings')
@login_required
def adminUserSettings():
    if (session.get('is_admin', None) != 'Y'):
        return render_template('homepage.html')
    else:
        return render_template('adminUserSettings.html')


# shows all wishlists associated with user, gathers required info for user to view wishlist
@app.route('/myWishlists', methods=['GET', 'POST'])
@login_required
def currentLists():
    user_id = session.get('user_id', None)
    if request.method == 'POST':
        session['list_id'] = request.form['list_id']
        return redirect(url_for('view_list'))
    return render_template('currentLists.html', user_id=user_id)


# shows all items in current wishlist, linked from myWishlists
@app.route('/wishlist', methods=['GET', 'POST'])
@login_required
def view_list():
    user_id = session.get('user_id', None)
    list_id = session.get('list_id', None)
    # edit button currently does a post method, it'll simply just reload the page
    # store the item_id as part of the session and print it to the console
    if request.method == 'POST':
        session['item_id'] = request.form['item_id']
        return redirect(url_for('edit_item'))

    return render_template('myWishlist.html', user_id=user_id, list_id=list_id)


@app.route('/editItem', methods=['GET', 'POST'])
@login_required
def edit_item():
    itemform = CreateItemForm()
    user_id = session.get('user_id', None)
    list_id = session.get('list_id', None)
    item_id = session.get('item_id', None)
    item = Items.query.filter_by(item_id=item_id).one()
    # follow the advice outlined in the post about using the GET method
    # https://stackoverflow.com/questions/23712986/pre-populate-a-wtforms-in-flask-with-data-from-a-sqlalchemy-object
    if request.method == 'GET':
        itemform.item_name.data = item.item_name
        itemform.item_description.data = item.item_description
        itemform.image_url.data = item.image_url
        itemform.item_url.data = item.item_url
        itemform.item_priority.data = item.item_priority
        return render_template('editItem.html', itemform=itemform, item_id=item_id, user_id=user_id, list_id=list_id,
                               item_name=item.item_name)
    if itemform.validate_on_submit():
        item.item_name = request.form['item_name']
        item.item_description = request.form['item_description']
        item.image_url = request.form['image_url']
        item.item_url = request.form['item_url']
        item.item_priority = request.form['item_priority']
        # Flask-SQLAlchemy adds to database here
        db.session.commit()
        # create a message to send to the template
        message = f"Item was updated."
        return render_template('editItem.html', message=message)
    else:
        # show errors
        for field, errors in itemform.errors.items():
            for error in errors:
                flash("Error in {}: {}".format(
                    getattr(itemform, field).label.text,
                    error
                ), 'error')
        return render_template('createItem.html', itemform=itemform)


# currently has no userchecking, fix later
@app.route('/deleteItem', methods=['POST'])
@login_required
def deleteItem():
    iid = request.form['item_id']
    item = Items.query.filter_by(item_id=iid).one()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('view_list'))


@app.route('/logout')
def logout():
    logout_user()
    session.pop('user_id')
    # only try to pop list_id if it's been set, otherwise we get an error
    if session.get('list_id'):
        session.pop('list_id')
    if session.get('is_admin'):
        session.pop('is_admin')
    return redirect(url_for('login'))


@app.route('/deleteList', methods=['POST'])
@login_required
def deletelist():
    lid = request.form['list_id']
    user_id = session.get('user_id', None)
    list = Lists.query.filter_by(list_id=lid).one()
    if list and (list.user_id == user_id):
        db.session.delete(list)
        db.session.commit()
    return redirect(url_for('currentLists'))


@app.route('/adminDeleteList', methods=['POST'])
@login_required
def adminDeletelist():
    lid = request.form['list_id']
    list = Lists.query.filter_by(list_id=lid).one()
    if (session.get('is_admin', None) == 'Y'):
        db.session.delete(list)
        db.session.commit()
    return redirect(url_for('adminListSettings'))


@app.route('/adminDeleteUser', methods=['POST'])
@login_required
def adminDeleteUser():
    uid = request.form['user_id']
    user = Users.query.filter_by(user_id=uid).one()
    if (session.get('is_admin', None) == 'Y'):
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('adminUserSettings'))


@app.route('/deleteSelf', methods=['GET'])
@login_required
def deleteSelf():
    uid = session.get('user_id', None)
    user = Users.query.filter_by(user_id=uid).one()
    if user:
        logout_user()
        session.pop('user_id')
        session.pop('list_id')
        session.pop('is_admin')
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('login'))


# Route for getting friends list
@app.route('/Friends')
def getFriends():
    user_id = session.get('user_id', None)
    friends = Friends.query.filter_by(user_id=user_id).all()
    return jsonify(friends)


# friends page route
@app.route('/friendsList', methods=['GET', 'POST'])
def friendspage():
    friendform = CreateFriendForm()
    if friendform.validate_on_submit():
        uid = session.get('user_id', None)
        fun = request.form['fusername']
        toadd = Users.query.filter_by(username=fun).first()
        exists = db.session.query(Friends.friend_id).filter_by(user_id=uid).first() is not None
        if toadd and not exists:
            newfriend = Friends(user_id=uid, friend_id=toadd.user_id, fusername=fun)
            db.session.add(newfriend)
            db.session.commit()
            return render_template('friends.html', friendform=friendform)
        else:
            flash('User not found or already friended')
    return render_template('friends.html', friendform=friendform)


# Still need to do something with this
@app.route('/friendsWishLists', methods=['POST'])
@login_required
def friendsWishLists():
    friend = Users.query.filter_by(user_id=request.form['friend_id']).first()
    session['friend_un'] = friend.username
    session['friend_id'] = request.form['friend_id']
    return render_template('FListSel.html', friend_id=session.get('friend_id', None))


@app.route('/Fwishlist', methods=['POST'])
@login_required
def view_flist():
    user_id = session.get('friend_id', None)
    list_id = request.form['list_id']
    return render_template('FWishlist.html', user_id=user_id, list_id=list_id)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
