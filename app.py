# app.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to our Wishlist app!</h1>"

@app.route('/test/')
def index():
    return "<h1>Testing on new branch...</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)