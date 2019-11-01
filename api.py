import datetime
import re
import smtplib
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS

from interface_new import *

app = Flask(__name__)
# cors = CORS(app, resources={r"/*": {"origins": "http://10.54.24.83"}}, supports_credentials=True)  # cors
app.config['SECRET_KEY'] = "{\xdb\x86\xa4\x0f\x0f\xd6\x9f'($\x87\x89\xafUyX\xb0\x01\x96 \xe1W\xf4"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if check_token()[0]:
            return jsonify({'msg': 'Token is Invalid', "status": 'Login Failed'})
        return f(*args, **kwargs)

    return decorated


def check_token():
    if 'token' in request.headers:
        token = request.headers['token']
    else:
        print('Token is Missing')
        return [False]
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        current_user = face_encodings.find_one({'key_id': data['key_id']})
        if current_user is not None:
            return [True, current_user['name']]
        else:
            return [False]
    except:
        print('Token is Invalid')
        return [False]


@app.route('/users/login/', methods=['POST'])
def login():
    username = request.form['username']
    pin = request.form['pin']
    if username and pin:
        target_user = face_encodings.find_one({'name': re.compile(username, re.IGNORECASE)})
        if target_user is not None:
            sha = hashlib.sha256(str(pin).encode("utf-8")).hexdigest()
            md_pass = hashlib.md5(str(sha).encode("utf-8")).hexdigest()
            if md_pass == target_user['pin']:
                token = jwt.encode(
                    {
                        'key_id': target_user['key_id'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)
                    },
                    app.config['SECRET_KEY'],
                    algorithm='HS256',
                )
                return jsonify({'msg': 'Success', 'token': token.decode('UTF-8'), 'status': 'Success'})
    return jsonify({'msg': 'Username or Password Invalid', "status": 'Login Failed'})


@app.route('/keep_alive/')
def keep_alive():
    authenticated = check_token()[0]
    return jsonify({'status': 'Success', 'msg': 'The backend server is started', 'Authenticated': authenticated})


@app.route('/unlock/', methods=['POST'])
def unlock():
    token_check = check_token()
    if token_check[0]:
        open_lock(token_check[1])
        return jsonify({'status': 'Success', 'msg': 'Lock should be Opened'})
    else:
        return jsonify({'msg': 'Token is Invalid', "status": 'Login Failed'})


@app.route('/feedback/', methods=['POST'])
def feedback():
    name = request.form['name']
    email = request.form['email']
    msg = request.form['msg']

    user = 'michael1120040819@gmail.com'
    pwd = 'yvwlabqudswllfqg'

    email_text = """
    Feedback from Facial recognition system!
    \
    From: %s
    Email: %s

    %s
    """ % (name, email, msg)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user, pwd)
        server.sendmail('Michael', 'maizhe.yang@saintandrews.net', email_text)
        server.close()

        print('Email sent!')
        return jsonify({'status': 'Success', 'msg': 'Sent!'})
    except:
        print('Something went wrong...')
        return jsonify({'status': 'Failed', 'msg': 'Failed'})


if "__main__" == __name__:
    app.run(port=4567, host='0.0.0.0', debug=True)
