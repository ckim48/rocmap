from flask import render_template, request, json, redirect, url_for, jsonify, Blueprint
import pymysql
import bcrypt
from mapapp import app
from mapapp.view import authentication
import logging
import datetime
import uuid
import re


bp = Blueprint('pfcourse', __name__);

@app.route('/pfSchool', methods=['POST'])
def pfSchool():
    school = request.json['school']

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT DISTINCT department_desc FROM cdcs_2 WHERE school='+'\''+school+'\''+';')
    conn.commit()

    result_set = c.fetchall()
    conn.close()
    c.close()
    return jsonify({"value_1": result_set})

@app.route('/pfSchool_ase', methods=['POST'])
def pfSchool_ase():
    school = request.json['school']

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT DISTINCT department_desc FROM cdcs WHERE school='+'\''+school+'\''+';')
    conn.commit()

    result_set = c.fetchall()
    conn.close()
    c.close()
    return jsonify({"value_1": result_set})

# TEST_2 for ajax building courses
@app.route('/pfCourse', methods=['POST'])
def pfCourse():
    # get the building id from test_2.html
    dpt = request.json['department']

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT num,title FROM CS_course WHERE major='+'\''+dpt+'\''+';')
    conn.commit()

    result_set = c.fetchall()
#   str(result_set)
    conn.close()
    c.close()
    return jsonify({"value_1": result_set})
#    return json.dumps({"value_1": result_set})
# END of TEST_2

@app.route('/infoCourse', methods=['POST'])
def infoCourse():
    # get the building id from test_2.html
    info_course = request.json['Course']

    # separate the string into department and course_num
    course = info_course.upper()

    if " " in course:
        indSpace = course.index(" ")
        department = course[:indSpace]
        course = course[indSpace + 1:]
        #course = course.split(" ")
    else:
        department = course[:-3]
        course = course[-3:]
#    department = course[0]
#    course = course[1]

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT instructor, prereq FROM cdcs WHERE department = %s AND course_num = %s;', (department, course))
    conn.commit()

    result_set = c.fetchall()
    c.close()
    conn.close()
    return jsonify({"value_1": result_set})

@app.route('/addcourse', methods=['POST'])
def addCourse():
    department = request.form['department']
    course = request.form['course']

    if department is None:
        return jsonify({"success" : "no"})
    if course is None:
        return jsonify({"success" : "no"})
    department = department.upper()

    user = authentication.getUserData()

    if user is None:
        return jsonify({"success" : "no"})

    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('INSERT INTO users_courses (email, crn) VALUES (%s, (SELECT DISTINCT crn FROM cdcs WHERE department = %s AND course_num = %s));', (str(user['email']), department, course))
    conn.commit()

    c.close()
    conn.close()

    return jsonify({"success" : "yes"})

@app.route('/addcoursebycrn', methods=['POST'])
def addcoursebycrn():
    crn = request.form['crn']

    if crn is None:
        return jsonify({"success" : "no"})

    user = authentication.getUserData()

    if user is None:
        return jsonify({"success" : "no"})

    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('INSERT INTO users_courses (email, crn) VALUES (%s, %s);', (str(user['email']), str(crn)))
    conn.commit()

    c.close()
    conn.close()

    return jsonify({"success" : "yes"})

@app.route('/getusercourses', methods=['POST'])
def getusercourses():
    user = authentication.getUserData()

    if user is None:
         return jsonify({"success" : "no"})

    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT * FROM cdcs WHERE crn IN (SELECT crn FROM users_courses WHERE email = %s);', str(user['email']))
    conn.commit()
    result_set = c.fetchall()
    c.close()
    conn.close()

    return jsonify({"success" : "yes", "courses" : result_set})

@app.route('/deletecourse', methods=['POST'])
def deletecourse():
    crn = request.form['crn']
    user = authentication.getUserData()

    if user is None:
         return jsonify({"success" : "no"})

    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('DELETE FROM users_courses WHERE email = %s AND crn = %s;', (str(user['email']), crn));
    conn.commit()

    c.close()
    conn.close()

    return jsonify({"success" : "yes"})

@app.route('/getcrnofcourse', methods=['POST'])
def getcrnofcourse():
    course = request.form['course']
    department = request.form['department']

    if course is None or department is None:
        return jsonify({"success" : "no"})

    course = course.upper()
    department = department.upper()

    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT crn FROM cdcs WHERE course_num = %s AND department = %s;', (str(course), str(department)));
    conn.commit()

    result_set = c.fetchall()

    c.close()
    conn.close()

    if result_set is None:
        return jsonify({"success" : "no"})
    else:
        return jsonify({"success" : "yes", "crns" : result_set})

@app.route('/getcrnofcourse2', methods=['POST'])
def getcrnofcourse2():
    info_course = request.form['course']

    if info_course is None:
        return jsonify({"success" : "no"})

    course = info_course.upper()

    if " " in course:
        indSpace = course.index(" ")
        department = course[:indSpace]
        course = course[indSpace + 1:]
        #course = course.split(" ")
    else:
        department = course[:-3]
        course = course[-3:]

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT crn FROM cdcs WHERE department = %s AND course_num = %s;', (department, course))
    conn.commit()

    result_set = c.fetchall()
    c.close()
    conn.close()
    if result_set is None:
        return jsonify({"success" : "no"})
    else:
        return jsonify({"success" : "yes", "crns" : result_set})

@app.route('/getcoursesfromdepartment', methods=['POST'])
def getdepartmentcourses():
    depart = request.form['department']
    if depart is None:
        return jsonify({"success" : "no"})
    
    department = str(depart).upper()

    # connect to db_course database
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()

    c.execute('SELECT * FROM cdcs WHERE department = %s;', (department))
    conn.commit()

    result_set = c.fetchall()
    c.close()
    conn.close()
    if result_set is None:
        return jsonify({"success" : "no"})
    else:
        return jsonify({"success" : "yes", "courses" : result_set})