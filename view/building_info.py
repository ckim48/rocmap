from flask import render_template, request, json, redirect, url_for, jsonify, Blueprint
import pymysql
import bcrypt
from mapapp import app
from mapapp.view import authentication
import logging
import datetime
import uuid
import re


bp = Blueprint('bdInfo', __name__)

# TEST_1 for localStorage
@app.route('/test1')
def test1():
    return render_template('test.html')


#        return "Successful!"
# END of TEST_1


# TEST_2 for ajax building courses
@app.route('/test2')
def test2():
    return render_template('test_2.html')


@app.route('/bdInfo', methods=['POST'])
def bdInfo():
    # get the building id from test_2.html
    bdName = request.json['name']

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT department,course_num,course_title,instructor FROM cdcs WHERE building='+'\''+bdName+'\''+';')
    conn.commit()

    result_set = c.fetchall()
#   str(result_set)
    c.close()
    conn.close()
    return jsonify({"value_1": bdName, "value_2": result_set})
#    return json.dumps({"value_1": result_set})
# END of TEST_2

@app.route('/mapCourse', methods=['POST'])
def mapCourse():
    # get the building id from test_2.html
    c_name = request.json['Course']

    # separate the string into department and course_num
    r = re.compile("([a-zA-Z]+)([0-9]+)")
    dpt = r.match(c_name).group(1)
    num = r.match(c_name).group(2)

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT building FROM cdcs WHERE department='+'\''+dpt+'\''+' AND course_num='+'\''+num+'\''+';')
    conn.commit()

    result = c.fetchall()
#   str(result_set)
    c.close()
    conn.close()
    return jsonify({"value_1": result})

@app.route('/getcoursebuildings', methods=['POST'])
def getcoursebuildings():
    course = request.form['course']
    course = course.upper()
    department = '*'
    if " " in course:
        indSpace = course.index(" ")
        department = course[:indSpace]
        course = course[indSpace + 1:]
    else:
        department = course[:-3]
        course = course[-3:]
    print(course + '   ' + department)
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT DISTINCT building FROM cdcs WHERE department = %s AND course_num = %s;', (department, course))

    result = c.fetchall()

    c.close()
    conn.close()

    if result is None:
        return jsonify({"hasResult" : "no"})
    else:
        return jsonify({"hasResult" : "yes", "buildings" : result})

@app.route('/getuserbuildings', methods=['POST'])
def getuserbuildingsajax():
    user = authentication.getUserData()
    if user is None:
        return jsonify({"hasResult" : "no"})
    else:
        conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
        c = conn.cursor()
        email = user['email']

        c.execute('SELECT DISTINCT building FROM cdcs WHERE crn IN (SELECT crn FROM users_courses WHERE email = %s);', (email))

        result = c.fetchall()

        c.close()
        conn.close()

        if result is None:
            return jsonify({"hasResult": "no"})
        else:
            return jsonify({"hasResult": "yes", "buildings": result})

def getuserbuildings():
    user = authentication.getUserData()
    if user is None:
        return jsonify({"hasResult": "no"})
    else:
        conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
        c = conn.cursor()
        email = user['email']

        c.execute('SELECT DISTINCT building FROM cdcs WHERE crn IN (SELECT crn FROM users_courses WHERE email = %s);', (email))

        result = c.fetchall()

        c.close()
        conn.close()

        return result