# app.py
from flask import Flask, request, jsonify
app = Flask(__name__)

#root route
@app.route('/')
def index():
    return "<h1>Welcome to our Wishlist app!</h1>"

#example json return
@app.route('/json-test')
def returnJson():
    return jsonify({'test':'var'})

if __name__ == '__main__':
    app.run(threaded=True, port=5000)