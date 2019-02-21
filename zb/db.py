
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/json/<cid>',methods=['GET'])
def json(cid):
    ip = request.remote_addr
    return jsonify({'cid':cid,'ip':ip})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
