from datetime import datetime
from flask import jsonify, request

from Api import mysql
from Api.admin import admin


@admin.route("/api/ticketInsert",methods=["post"])
def ticketInsert():
    if not (request.json and request.json["uid"],request.json["type"]):
        return "not enough input",201
    cur=mysql.connection.cursor()
    try:
        cur.execute("insert into tickets(uid,type,date,status) values(%s,%s,%s,%s)",
                    (request.json["uid"], request.json["type"], datetime.now(),False))

        mysql.connection.commit()
        cur.execute("select id from tickets where uid=%s order by date DESC limit 1",(request.json["uid"],))
        tid=cur.fetchone()
        tid=tid[0]
        msg=generateMessage(request.json["type"])
        cur.execute("insert into messages(tid,message,sid) values(%s,%s,%s)",(tid,msg,request.json["uid"]))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(e)
        return jsonify(str(e)),201
    return "successful",200

@admin.route("/api/ticketDisplay",methods=["get","post"])
def ticketDisplay():
    cur=mysql.connection.cursor()
    try:
        if request.method=='post':
            if (request.json.get("uid")):
                cur.execute("select * from tickets where uid=%s", (request.json["uid"],))

        else:
            cur.execute("select * from tickets")
        rows=cur.fetchall()
        names={}
        ids=[]
        for row in rows:
            if row[1] not in ids:
                ids.append(row[1])
        for id in ids:
            cur.execute("select name from user where id=%s",(id,))
            d=cur.fetchone()
            names[id]=d[0]
        messages={}
        for row in rows:
            cur.execute("select message from messages where tid=%s",(row[0],))
            msg=cur.fetchone()
            messages[row[0]]=msg[0]
        cur.close()

        data={row[0]:[names[row[1]],row[2],timeformat(row[3]),messages[row[0]],row[4]] for row in rows}
        print(data)
        return jsonify(data),200
    except Exception as e:
        print(e)
        return jsonify(str(e)),201

@admin.route("/api/ticketUpdate",methods=["post"])
def ticketUpdate():
    if not (request.json["tid"]):
        return "tid missing",201
    cur=mysql.connection.cursor()
    try:
        cur.execute("update tickets set status=True where id=%s",(request.json["tid"],))
        mysql.connection.commit()
        cur.close()
        return jsonify("successful"),200
    except Exception as e:
        return jsonify(str(e)),201

@admin.route("/api/sendMessage1",methods=["post"])
def sendMessage():
    if not (request.json and request.json["tid"],request.json["message"]):
        return "not enough input",201
    cur=mysql.connection.cursor()
    try:
        cur.execute("insert into messages(tid,message,sid) values(%s,%s,%s)",
                    (request.json["tid"], request.json["message"],request.json["sid"]))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        return jsonify(e),201
    return "successful",200

@admin.route("/api/readMessage",methods=["get","post"])
def readMessage():
    print("calling")
    if not (request.json.get("tid")):
        return "missing ticket_id",201
    cur=mysql.connection.cursor()
    try:
        cur.execute("select * from messages where tid=%s",(request.json["tid"],))
        rows=cur.fetchall()
        cur.close()
        data={row[0]:[row[1],row[2],row[3]] for row in rows}
        return jsonify(data),200
    except Exception as e:
        return jsonify(e),201

def generateMessage(type):
    if type=="leave":
       return " want leave for"

def timeformat(unixDate):
    return unixDate.strftime("%b %d %Y %H:%M")
