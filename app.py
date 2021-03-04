# app.py
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Welcome to our Wishlist app!</h1>"

#example template
@app.route('/template-test')
def test():
    return render_template("test.html")

if __name__ == '__main__':
    app.run(threaded=True, port=5000)