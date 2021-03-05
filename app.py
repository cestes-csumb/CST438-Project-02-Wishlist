# app.py
# Authors: Chris Estes
from flask import Flask, request, jsonify, render_template
import pymysql.cursors

app = Flask(__name__)

#Database connection test sample
def execute(sql, isSelect=True):
    conn = pymysql.connect(host='s0znzigqvfehvff5.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
                           port=3306,
                           user='e4l6k1v8lciacn5x',
                           password='p98yj0ifq773irmb',
                           db='qwicl09ul8c9lcw1',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
    result = None
    try:
        with conn.cursor() as cursor:
            if isSelect:
                cursor.execute(sql)
                result = cursor.fetchall()
                print(f"result = {result}")
            else:
                cursor.execute(sql)
                result = conn.insert_id()
                conn.commit()
    finally:
        conn.close()
    return result


# root route
@app.route('/')
def index():
    return "<h1>Welcome to our Wishlist app!</h1>"


# example template
@app.route('/template-test')
def test():
    return render_template("test.html")


# example json return
@app.route('/json-test')
def returnJson():
    return jsonify({'test': 'var'})


#route for testing external db connection
@app.route('/dbtest')
def getSomeStuff():
    sql = f"select * from fp_account;"
    stuff = execute(sql, True)
    return jsonify(stuff)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
