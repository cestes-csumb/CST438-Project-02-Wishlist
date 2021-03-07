# app.py
# Authors: Chris Estes
from dataclasses import dataclass

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://pf3n93rxwh14176k:zoat5w7a3vgn4rgl@ao9moanwus0rjiex.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/k98fz84q0v1bbm9t"
db = SQLAlchemy()
app.secret_key = 'topsecret'
db.init_app(app)


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
    user_id = db.Column(db.Integer, forign_key=True)
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
    list_id = db.Column(db.Integer, forign_key=True)
    marked_user_id = db.Column(db.Integer, forign_key=True)


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


@app.route('/createAccount')
def createAccount():
    return render_template("createAccount.html")


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


# route for getting Users from db
@app.route('/getUsers')
def getUsers():
    users = Users.query.all()
    return jsonify(users)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
