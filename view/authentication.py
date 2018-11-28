from flask import render_template, request, json, redirect, url_for, jsonify, Blueprint
import pymysql
import bcrypt
from mapapp import app
import logging
import datetime
import uuid
import os
from shutil import copyfile

bp = Blueprint('auth', __name__);


def getUserData(email = None):
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor(pymysql.cursors.DictCursor)
    if (email is None):
        if is_user_in_session():
            cookie_value = request.cookies.get('session_key')
            if cookie_value:
                c.execute("SELECT * FROM users WHERE session_key = %s;", (cookie_value))
                conn.commit()
                row = c.fetchone()
                c.close()
                conn.close()
                if row is not None:
                    return row;
                else:
                    return None
        else:
            return None
    else:
        c.execute("SELECT * FROM users WHERE email = %s;", (email))
        conn.commit()
        row = c.fetchone()
        c.close()
        conn.close()
        if row is not None:
            return row;
        else:
            return None


@app.route('/authenticateAJAX', methods=['POST'])
def authenticateAJAX():
    if is_user_in_session():
        return json.dumps({'status': 'OK', 'authOK': 'OK', 'message': "Already Logged in"});
    else:
        _email = request.form['usr_email']
        _password = request.form['usr_password']
        # _chk_box = request.form.getlist['chk_box']
        if _email and _password:
            conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')

            c = conn.cursor()
            c.execute("SELECT pw FROM users WHERE email = %s;", (_email))
            conn.commit()
            _password = 'b' + _password
            attempt_user = False  # if user is authenticated
            row = c.fetchone()
            if row is not None:
                acc_pw = str(row[0])
                attempt_user = bcrypt.checkpw(_password.encode('utf-8'), acc_pw.encode('utf-8'))
            if attempt_user:
                c.execute("SELECT name FROM users WHERE email = %s;", (_email))
                conn.commit()
                row_1 = c.fetchone()
                if row_1 is not None:
                    name = str(row_1[0])
                    cookie_value = uuid.uuid4()
                    cookie_value2 = str(cookie_value)
                    c.execute('UPDATE users SET session_key = %s WHERE email = %s;', (cookie_value2, _email))
                    conn.commit()
                    if request.form.get('chk_box'):
                        expire_date = datetime.datetime.now()
                        expire_date = expire_date + datetime.timedelta(days=30)
                        c.close()
                        conn.close()
                        return json.dumps({'status': 'OK', 'authOK': 'OK', 'cookie': cookie_value2, 'expires': expire_date});
                    else:
                        c.close()
                        conn.close()
                        return json.dumps({'status': 'OK', 'authOK': "OK", 'cookie': cookie_value2, 'expires': ""});
                else:
                    c.close()
                    conn.close()
                    return json.dumps({'status': 'OK', 'authOK': 'NO', 'message': "An Error Occurred.<br>Please try again later"});
            else:
                c.close()
                conn.close()
                return json.dumps({'status': 'OK', 'authOK': 'NO', 'message': "Incorrect Credentials.<br>Please check your email and password"});
        else:
            return json.dumps({'status': 'OK', 'authOK': 'NO', 'message': "Please fill in both email and password"});


# DEPRECATED PLEASE REMOVE AT SOME POINT - 2017.11.15
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # if the user is in session, redirect to map
    if is_user_in_session():
        return redirect(url_for('map'))
    else:
        _email = request.form['usr_email']
        _password = request.form['usr_password']
        # _chk_box = request.form.getlist['chk_box']
        if _email and _password:
            conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')

            c = conn.cursor()
            c.execute("SELECT pw FROM users WHERE email = %s;", (_email))
            conn.commit()
            _password = 'b' + _password
            attempt_user = False  # if user is authenticated
            row = c.fetchone()
            if row is not None:
                acc_pw = str(row[0])
                attempt_user = bcrypt.checkpw(_password.encode('utf-8'), acc_pw.encode('utf-8'))
            if attempt_user:
                c.execute("SELECT name FROM users WHERE email = %s;", (_email))
                conn.commit()
                row_1 = c.fetchone()
                if row_1 is not None:
                    name = str(row_1[0])

                    if request.form.get('chk_box'):
                        cookie_value = uuid.uuid4()
                        cookie_value2 = str(cookie_value)
                        # test = '12345678'
                        c.execute(
                            'UPDATE users SET session_key= ' + '\'' + cookie_value2 + '\'' + ' Where email = ' + '\'' + _email + '\'' + ';')
                        conn.commit()
                        expire_date = datetime.datetime.now()
                        expire_date = expire_date + datetime.timedelta(days=30)
                        response = redirect(url_for("session"))
                        response.set_cookie('Cookies', cookie_value2, expires=expire_date)
                        return response
                    else:
                        cookie_value = uuid.uuid4()
                        cookie_value2 = str(cookie_value)
                        c.execute(
                            'UPDATE users SET session_key= ' + '\'' + cookie_value2 + '\'' + ' Where email = ' + '\'' + _email + '\'' + ';')
                        conn.commit()
                        response = redirect(url_for("session"))
                        response.set_cookie('Cookies', cookie_value2)
                        return response
                else:
                    return render_template('login.html', authFailure="An Error occured")
            else:
                return render_template('login.html', authFailure="Incorrect credentials. Check your login")
        else:
            return render_template('login.html', authFailure="Please fill both email and password")


def is_user_in_session():
    cookie_value = request.cookies.get('session_key')
    if cookie_value:
        conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
        c = conn.cursor()
        user = c.execute("SELECT session_key FROM users WHERE session_key = %s;", (cookie_value))
        conn.commit()
        c.close()
        conn.close()
        if user:
            return True
        else:
            return False
    else:
        return False


@app.route('/register')
def register():
    if is_user_in_session():
        return redirect(url_for('map'))
    else:
        return render_template('register.html')


@app.route('/registerAJAX', methods=['POST'])
def registerUserAJAX():
    if is_user_in_session():
        return redirect(url_for('map'))
    else:
        _name = request.form['name']
        _email = request.form['email']
        _password = request.form['password']
        _major = request.form['major']

        if _name and _email and _password:
            conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
            _password = 'b' + _password
            _password = _password.encode('utf-8')
            pw = bcrypt.hashpw(_password, bcrypt.gensalt())
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = %s;", (_email))
            conn.commit()
            if not c.rowcount:
                c.execute("SELECT id FROM majors WHERE name = %s;", (_major))
                conn.commit()
                row = c.fetchone()
                if row is not None:

                    file_path = "/home/ubuntu/flaskapp/mapapp/static/profile_pic"
                    directory = file_path + "/"+_email
                    directory2 = directory + "/icon-profile.png"
                    if not os.path.exists(directory):
                        os.mkdir(directory)
                    copyfile('/home/ubuntu/flaskapp/mapapp/static/icon-profile.png', directory2)
                    filename = "icon-profile.png"
                    path = _email+"/"+filename
                    c.execute("INSERT INTO users (email, name, pw,profile_pic ,major) VALUES (%s, %s, %s, %s, %s);", (_email, _name, pw.decode('utf-8'), path, str(row[0])))
                    conn.commit()
                    c.close()
                    conn.close()
                    return json.dumps({'status':'OK','regOK' : 'OK', 'message': _name + ", you've been successfully registered."});
                else:
                    c.close()
                    conn.close()
                    return json.dumps({'status':'OK','regOK' : 'NO', 'message': "Unknown Major."});
            else:
                c.close()
                conn.close()
                return json.dumps({'status':'OK','regOK' : 'NO', 'message': "Email already exists!"});
        else:
            return json.dumps({'status':'OK','regOK' : 'NO', 'message': "Unknown Email, Password, Major, etc."});


@app.route('/registerUser', methods=['POST'])
def registerUser():
    if is_user_in_session():
        return redirect(url_for('map'))
    else:
        _name = request.form['name']
        _email = request.form['email']
        _password = request.form['password']
        _major = request.form['major']

        if _name and _email and _password:
            conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
            _password = 'b' + _password
            _password = _password.encode('utf-8')
            pw = bcrypt.hashpw(_password, bcrypt.gensalt())
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = %s;", (_email))
            conn.commit()
            if not c.rowcount:
                c.execute("SELECT id FROM majors WHERE name = %s;", (_major))
                conn.commit()
                row = c.fetchone()
                if row is not None:
                    c.execute("INSERT INTO users (email, name, pw, major) VALUES (%s, %s, %s, %s);",(_email, _name, pw.decode('utf-8'), str(row[0])))
                    conn.commit()
                    c.close()
                    conn.close()
                    return render_template('login.html', authFailure="You're Successfully registered.")
                else:
                    c.close()
                    conn.close()
                    return render_template('login.html', authFailure="Something went wrong. Major unknown.")
            else:
                c.close()
                conn.close()
                return render_template('login.html', authFailure="The email you've entered is already registered.")
        else:
            return render_template('register.html', authFailure="Please fill email, name, and password")


# add the logout function here
@app.route('/logout')
def logout():
    #	response.headers['Cache-Control']='no-cache,no-store,must-revalidate'
    #	response.headers['Pragma']='no-cache'
    if is_user_in_session():
        cookie_value = request.cookies.get('session_key')
        if cookie_value:
            conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
            c = conn.cursor()
            c.execute("UPDATE users SET session_key = NULL WHERE session_key = %s", (cookie_value))
            conn.commit()
            c.close()
            conn.close()
    return redirect(url_for('map'))
