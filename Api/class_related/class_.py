from datetime import datetime, timedelta

from flask import Flask,render_template,session
from flask import jsonify, request, Response

from Api import mysql
from . import class_related


@class_related.route("/api/addHistory", methods=["Post"])
def addHistory():
    if not (request.json and request.json.get('sid') and request.json.get('tid') and request.json.get(
            'cid') and (request.json.get('status') != None)):
        return "Error", 201
    cur = mysql.connection.cursor()
    try:

        cur.execute("insert into history(sid,tid,cid,status,time) values(%s,%s,%s,%s,%s)", (
            request.json.get('sid'), request.json.get('tid'), request.json.get('cid'),
            request.json.get('status'),request.json.get("time")))
        mysql.connection.commit()
    except Exception as e:
        return str(e), 201
    return 'Successful', 200


@class_related.route("/api/readHistory", methods=["Post"])
def readHistory():
    if not (request.json and (request.json.get('tid') or request.json.get("sid"))):
        return "Error", 201
    cur = mysql.connection.cursor()
    try:
        lastweek = datetime.today() - timedelta(7)
        if (request.json.get("tid")):
            cur.execute("select e.schedule_id,h.time,h.status from history h "
                        "inner join enroll e on e.cid=h.cid and (h.cid,h.time) in "
                        "(select cid,max(time) from history where tid=%s group by cid) ", (
                            request.json.get('tid'),))
        else:
            cur.execute("select e.schedule_id,h.time,h.status from history h "
                        "inner join enroll e on e.cid=h.cid and (h.cid,h.time) in "
                        "(select cid,max(time) from history where sid=%s group by cid) ", (
                            request.json.get('sid'),))

        rows = cur.fetchall()

        data = {row[0]: [int(row[1])>lastweek.microsecond, row[2]] for row in rows}
        return jsonify(data)
    except Exception as e:
        return str(e), 201


@class_related.route("/api/readCourseHistory",methods=["post"])
def readCourseHistory():
    data={}
    cur = mysql.connection.cursor()
    try:
        query=None

        if(request.json.get("id")):
            q = "select id from parents where uid=" + str(request.json.get("id"))
            cur.execute(q)
            pid = cur.fetchone()
            query="select * from enroll where sid in (select uid from students where pid={})".format(pid[0])
            cur.execute(query)
        else:
            cur.execute("select * from enroll")
        enrollData=cur.fetchall()
        i=0
        for row in enrollData:
            lst=[]
            cur.execute("select name from user where id=%s",(row[0],))
            d=cur.fetchone()
            lst.append(d[0])
            cur.execute("select name from user where id=%s", (row[2],))
            d = cur.fetchone()
            lst.append(d[0])
            cur.execute("select title from courses where id=%s", (row[1],))
            d = cur.fetchone()
            lst.append(d[0])
            cur.execute("select * from history where sid=%s and cid=%s and tid=%s", (row[0],row[1],row[2]))
            d = cur.fetchall()
            lst2=[[row[0],row[4],timeformat(row[5]),row[6]]for row in d]
            lst.append(lst2)
            data[i]=lst
        return jsonify(data)
    except Exception as e:
        return str(e), 201

def timeformat(unixDate):
    from datetime import datetime, timedelta
    return (datetime(1970, 1, 1) + timedelta(seconds=int(unixDate)/1000)).strftime("%b %d %Y %H:%M")

@class_related.route("/api/sendMessage", methods=["post"])
def sendMessage():
    if not (request.json and request.json.get("sid") and request.json.get("rid") and request.json.get("msg")):
        return "error", 201
    cur = mysql.connection.cursor()
    today=datetime.today()
    try:
        cur.execute("insert into messages (sid,rid,msg,time) values(%s,%s,%s,%s)",
                    (request.json.get("sid"), request.json.get("rid"), request.json.get("msg"), today))
        mysql.connection.commit()
    except Exception as e:
        return e,201
    cur.close()
    return jsonify("successful"),200

@class_related.route("/api/readMessages", methods=["post"])
def readMesages():
    if not (request.json and request.json.get("id")):
        return "error", 201
    cur = mysql.connection.cursor()

    cur.execute("select sid,rid,msg from messages where sid=%s or rid=%s order by time desc", (request.json.get('id'),request.json.get('id')))

    rows = cur.fetchall()
    i = 0
    data = [ {'sid':rows[i][0],'rid':rows[i][1],'msg':rows[i][2]} for i in range(len(rows))]
    cur.close()
    return jsonify(data)

@class_related.route("/api/sendReqTutor", methods=["Post"])
def sendReqTutor():
    if not (request.json and request.json.get("Email") and request.json.get("Password") and request.json.get(
            "TimeZone")):
        return "Error", 201

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Tutor(Name,Email,Password,TimeZone) VALUES (%s, %s,%s,%s)" \
                , (request.json.get("Name"), request.json.get("Email"), request.json.get("Password"),
                   request.json.get("TimeZone")))

    mysql.connection.commit()

    return "successful", 200


@class_related.route("/api/readTutorRequest")
def readTutorRequest():

    cur = mysql.connection.cursor()

    cur.execute("select * from Tutor")

    rows = cur.fetchall()
    i = 0
    data={i:rows[i] for i in range(len(rows))}
    cur.close()
    return jsonify(data)

@class_related.route("/api/deleteTutorReq", methods=["post"])
def deleteTutorReq():
    if not (request.json and request.json.get("id")):
        return "error", 201
    cur = mysql.connection.cursor()

    try:
        cur.execute("delete from Tutor where id=%s", (request.json.get("id"),))

        mysql.connection.commit()
    except Exception as e:
        return e,201
    cur.close()
    return "successful",2

@class_related.route("/api/Read_Quran",methods=["post"])
def Read_Quran():

    cur = mysql.connection.cursor()
    try:
        cur.execute("select strt_ayat,endg_ayat,surah from ruku where id=%s",
                    (request.json.get("id"),))

        rows = cur.fetchall()
        strt_ayat = rows[0][0]
        endg_ayat = rows[0][1]
        surah = rows[0][2]
        cur.execute("select ayat_no,text,aya from quran_ayat where aya between %s and %s and sura=%s",
                    (strt_ayat, endg_ayat, surah))

    except Exception as e:
        return str(e),201
    rows = cur.fetchall()
    # data={}i=0
    # j=0
    # while(i<len(rows)):
    #     lst=[]
    #     lst2=[]
    #     for k in range(4):
    #         if i+k>=len(rows):
    #             break
    #         lst.append(rows[i+k][1])
    #         t=[]
    #         t.append(rows[i+k][0])
    #         st_verse=rows[i+k][2]
    #         s=st_verse.split(':')
    #         t.append(s[1])
    #         lst2.append(t)
    #
    #     data[j]=[lst2,lst]
    #     i=i+4
    #     j=j+1
    data={i:[rows[i][0],rows[i][2],rows[i][1]] for i in range(len(rows))}

    cur.close()
    return jsonify(data)


@class_related.route("/api/DisplayLessons")
def DisplayLessons():
    records={}
    cur = mysql.connection.cursor()
    try:
        cur.execute("select id,strt_ayat,endg_ayat,surah from ruku")

        rows = cur.fetchall()
        lst=[[row[0],row[1],row[2],row[3]] for row in rows]
        for i in range(len(lst)):
            cur.execute("select distinct arabic from quran_surah q inner join quran_ayat a on q.id=a.sura "
                        "where a.aya between %s and %s and sura=%s", (lst[i][1], lst[i][2], lst[i][3]))
            rows=cur.fetchall()
            records[i]=[lst[i][0],lst[i][1],lst[i][2],rows[0][0],lst[i][3]]
    except Exception as e:
        return str(e),201

    cur.close()
    return jsonify(records)

@class_related.route("/api/read_ResumeData",methods=["post"])
def read_ResumeData():
    records={}
    cur = mysql.connection.cursor()
    try:
        print(request.json)
        cur.execute("select ruku,surah from resume where sid=%s and cid=%s ",(request.json.get("sid"),request.json.get("cid")))
        row=cur.fetchone()
        print(row)
        cur.execute("select arabic from quran_surah where id=%s",(row[1],))
        row1=cur.fetchone()
    except Exception as e:
        return str(e),201
    try:
        records = {"id": row[0], "surahName": row1[0], "surahno": row[1]}
    except Exception as e:
        cur.execute("select arabic from quran_surah where id=%s", (1,))
        row1 = cur.fetchone()
        records={"id":1,"surahName":row1[0],"surahno":1}
    cur.close()
    return jsonify(records)


