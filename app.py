from flask import Flask, request, jsonify
app = FLASK(__name__)

@app.route('/')
def index():
    return "<h1> Wishlist App!</h1>"
    
if __name__ == '__main__':
    app.run(thread=True, port=5000)