import sys

from flask import Flask, request
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, join_room

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'ProjectDb'
from Api.user import user as user_blueprint
from Api.courses import courses as course_blueprint
from Api.class_related import class_related as class_blueprint
from Api.admin import admin as admin_blueprint
app.register_blueprint(user_blueprint)
app.register_blueprint(course_blueprint)
app.register_blueprint(class_blueprint)
app.register_blueprint(admin_blueprint)
rooms={}


@socketio.on('connect')
def connect():
    print("connected")
    room =  int(request.headers["user_id"])
    join_room(room)
    print(room)
    rooms[room] = room
    socketio.emit("message", str(room) + " user has joined", room=room)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', file=sys.stderr)
    socketio.emit('my_response', " FRom server", callback=messageReceived)

@socketio.on('join')
def on_join(data):
    room = data['user_id']

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']

@socketio.on('selectedAyat')
def selectedAyat(json):
    print(json)
    cur = mysql.connection.cursor()
    cur.execute("update resume set surah=%s,ayat=%s,ruku=%s where sid=%s and tid=%s and cid=%s",(json["surah"],json["ayat"],json["ruku"],json["sid"],json["tid"],json["cid"]))
    mysql.connection.commit()
    socketio.emit("selectAyat", {"ayat":json["ayat"],"scroll":json["scroll"]},room=json["sid"])

@socketio.on('selectedAyat')
def selectedAyat(json):
    print(json)
    cur = mysql.connection.cursor()
    cur.execute("update resume set surah=%s,ayat=%s,ruku=%s where sid=%s and tid=%s and cid=%s",(json["surah"],json["ayat"],json["ruku"],json["sid"],json["tid"],json["cid"]))
    mysql.connection.commit()
    socketio.emit("selectAyat", {"ayat":json["ayat"],"scroll":json["scroll"]},room=json["sid"])

@socketio.on('scroll')
def scroll(json):
    print(json)
    socketio.emit("scroll", json["index"],room=json["sid"])

@socketio.on('changeLesson')
def changeLesson(json):

    cur = mysql.connection.cursor()
    socketio.emit("changedLesson",json["ruku"],room=json["sid"])
    cur.execute("update resume set surah=%s,ayat=%s,ruku=%s where sid=%s and tid=%s and cid=%s",
                (json["surah"], json["ayat"], json["ruku"], json["sid"], json["tid"], json["cid"]))
    mysql.connection.commit()
    cur.execute("update history set lesson=%s where sid=%s and tid=%s and cid=%s",
                (json["ruku"], json["sid"], json["tid"], json["cid"]))
    mysql.connection.commit()

@socketio.on("call_user")
def call_user(data):
    print("cqll user")
    socketio.emit("call_made",data,room=data["id"])

@socketio.on("make_answer")
def make_answer(data):
    print("mzke answer")
    socketio.emit("answer_made",data,room=data["id"])

@socketio.on("send_ice")
def make_answer(data):
    print("mzke ice")
    socketio.emit("recieve_ice",data["ice"],room=data["id"])

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!',file=sys.stderr  )
@socketio.on('message')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my_response', json+" FRom server")


if __name__ == '__main__':
    socketio.run(app,host="192.168.8.29",port=5000)
