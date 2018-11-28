from flask import render_template, request, json, redirect, url_for, jsonify, Blueprint
from mapapp import app, views
from mapapp.view import authentication
from flask_socketio import SocketIO, emit
import pymysql
import datetime

bp = Blueprint('chat', __name__);

socketio = SocketIO(app)


class ChatMessage:
    def __init__(self, email, content, time):
        self.email = email
        self.content = content
        self.time = time
        self.name = authentication.getUserData(email)['name']
        self.photo = url_for('static', filename='profile_pic/' + str(authentication.getUserData(email)['profile_pic']))

@app.route('/chat')
def chat():
    if (authentication.is_user_in_session()):
        messages = getMessages()
        return render_template('chat.html', msg=messages, chatSize=len(messages))
    else:
        return views.index()


@socketio.on('text', namespace='/chatroom')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    row = authentication.getUserData()
    if (row is not None):
        profile_url = url_for('static', filename='profile_pic/' + str(row['profile_pic']))
        emit('message', {'photo': profile_url, 'name': str(row['name']), 'content': message['msgContent'], 'time': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}, broadcast=True)
        storeChat(row['email'], message['msgContent'])

    else:
        emit('message', {'photo': '', 'name': 'Connection Error', 'content': 'No key found', 'time': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}, broadcast=True)


def storeChat(email, content):
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor()
    c.execute("INSERT INTO chat (email, content) VALUES (%s, %s)", (email, content))
    conn.commit()
    c.close()
    conn.close()


def getMessages():
    messages = []
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute("SELECT * FROM chat ORDER BY time DESC LIMIT 30;")
    conn.commit()
    row = c.fetchone()
    while row is not None:
        messages.insert(0, ChatMessage(row['email'],row['content'], row['time']))
        row = c.fetchone()
    c.close()
    conn.close()
    return messages


@app.route('/getChatAJAX', methods=['POST'])
def getAjaxMessages(loaded=0):
    loadString = request.form['loadedMsgCount']
    loaded = int(loadString)
    messages = []
    conn = pymysql.connect(user='root', passwd='+6JSK+|S7*_wLoQi', db='rocmap')
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute("SELECT * FROM chat ORDER BY time DESC LIMIT " + str(loaded + 30) + ";")
    conn.commit()
    row = c.fetchone()
    count = 1
    while row is not None:
        if count > loaded:
            messages.insert(0, ChatMessage(row['email'],row['content'], row['time']))
        count += 1
        row = c.fetchone()

        # return "[" + ",".join((json.dumps(messages)))+ "]"
    jsonString = []
    for msg in messages:
        timeStr = str(msg.time.strftime("%Y-%m-%d %H:%M:%S"))
        jsonString.append({"name":  msg.name , "content": msg.content , "time":  timeStr, "photo": msg.photo})
    c.close()
    conn.close()
    return json.dumps(jsonString)
