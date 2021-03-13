# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for,flash, session

app = Flask(__name__)



#root route
@app.route('/wip', methods=['GET', 'POST'])
def loginpage():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'test' or request.form['password'] != 'test':
            error = 'Invalid Credentials. Try again or Create Account.'
        else:

            return redirect(url_for('wip_homepage'))
    return render_template('wip_loginpage.html', error=error)

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

@app.route('/logout')
def logout():
        return redirect(url_for('loginpage'))

#example template
@app.route('/template-test')
def wip_test():
    return render_template("test.html")

#example json return
@app.route('/json-test')
def returnJson():
    return jsonify({'test':'var'})

if __name__ == '__main__':
    app.run(threaded=True, port=5000)