# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for,flash, session

app = Flask(__name__)


@app.route('/wip_homepage')
def wip_homepage():
        return render_template("wip_homepage.html")

@app.route('/wip_createAccount')
def wip_createAccount():
        return render_template("wip_createAccount.html")

@app.route('/updateMerch')
def updateMerch():
        return render_template("updateMerch.html")

@app.route('/manageProduct')
def manageProduct():
        return render_template("manageProduct.html")

@app.route('/addProduct')
def addProduct():
        return render_template("addProduct.html")

@app.route('/profileSettings')
def profileSettings():
        return render_template("profileSettings.html")

@app.route('/wip_logout')
def wip_logout():
        return redirect(url_for('wip_loginpage'))

if __name__ == '__main__':
    app.run(threaded=True, port=5000)