# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

#root route
@app.route('/', methods=['GET', 'POST'])
def loginpage():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'test' or request.form['password'] != 'test':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('homepage'))
    return render_template('loginpage.html', error=error)

#example template
@app.route('/template-test')
def test():
    return render_template("test.html")

#example json return
@app.route('/json-test')
def returnJson():
    return jsonify({'test':'var'})

if __name__ == '__main__':
    app.run(threaded=True, port=5000)