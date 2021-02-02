from flask import Flask,render_template,session
from flask import jsonify, request, Response

from . import courses
from Api import mysql

@courses.route("/api/courses", methods=["post"])
def getCourses():
    if not (request.json and request.json.get('id') and request.json.get('role')):
        return "Error", 201

    cur = mysql.connection.cursor()
    if (request.json.get("role") == "student"):
        cur.execute("Select * from courses where id not in("
                    "select cid from request where sid=%s) and id not in "
                    "(select cid from enroll where sid=%s)",
                    (request.json.get('id'), request.json.get('id')))
    elif (request.json.get("role") == "tutor"):
        cur.execute("Select c.* from courses c where id not in (select cid from allocation where tid=%s)"
                    " and id not in (select cid from enroll where tid=%s)",
                    (request.json.get('id'), request.json.get('id')))

    rows = cur.fetchall()
    data = {row[0]: row[1] for row in rows}

    return jsonify(data)


@courses.route("/api/enroll", methods=['Post'])
def enroll():
    if not (request.json and request.json.get('sid') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("insert into enroll values(%s,%s)", (request.json.get('sid'), request.json.get('cid')))
    mysql.connection.commit()
    return 'Successful'


@courses.route("/api/tempEnroll", methods=['Post'])
def tempEnroll():
    if not (request.json and request.json.get('sid') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    millsEnd = (datetime.fromtimestamp(request.json.get("mills")) + timedelta(
        days=int(request.json.get("interval"))) * 7).timestamp()
    interval = millsEnd - request.json.get("mills")
    cur.execute("insert into tempEnroll values(%s,%s,%s,%s,%s,%s)", (
    request.json.get('sid'), request.json.get('tid'), request.json.get('cid'), request.json.get("schedule_id"),
    request.json.get('mills'), interval))
    mysql.connection.commit()
    return 'Successful'


@courses.route("/api/getAllocationCourses", methods=['post'])
def getalloocation():
    if not (request.json and request.json.get('tid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("select c.* from courses c inner join allocation a on "
                " c.id=a.cid where a.tid=%s ", (request.json.get("tid"),))
    rows = cur.fetchall()
    cur.execute("select e.cid from enroll e where e.tid=%s ", (request.json.get("tid"),))
    rows2 = cur.fetchall()
    elst = [row[0] for row in rows2]
    data = {i: [rows[i][0], rows[i][1], rows[i][0] in elst] for i in range(len(rows))}
    return jsonify(data)


@courses.route('/api/allocate', methods=['post'])
def allocate():
    if not (request.json.get('id') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    try:
        cur.execute("insert into allocation values(%s,%s)", (request.json.get('cid'), request.json.get('id')))
        mysql.connection.commit()
        return 'Successful'
    except Exception as e:
        return str(e)


@courses.route("/api/getEnrolledCourses", methods=["Post"])
def getEnrolledCourses():
    if not (request.json and request.json.get('sid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("select c.*,sc.day,sc.time,u.name from courses c inner join enroll e on c.id=e.cid "
                "inner join schedule sc on sc.id=e.schedule_id "
                "inner join user u on u.id=e.tid"
                " where e.sid=%s", (request.json.get("sid"),))
    rows = cur.fetchall()
    i = 0
    data = {i: rows[i] for i in range(len(rows))}
    return jsonify(data)


@courses.route("/api/unenroll", methods=['Post'])
def unenroll():
    if not (request.json and request.json.get('sid') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("delete from enroll where sid=%s and cid=%s", (request.json.get('sid'), request.json.get('cid')))
    mysql.connection.commit()
    return 'Successful'


@courses.route("/api/unallocate", methods=['Post'])
def unallocate():
    if not (request.json and request.json.get('tid') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("delete from allocation where tid=%s and cid=%s", (request.json.get('tid'), request.json.get('cid')))
    mysql.connection.commit()
    return 'Successful'


@courses.route("/api/submitTutor", methods=["Post"])
def submitTutor():
    if not (request.json and request.json.get("Email") and request.json.get("Password") and request.json.get(
            "TimeZone")):
        return "Error", 201

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO User(Name,Email,Password,Role,TimeZone) VALUES (%s, %s,%s,%s,%s)" \
                , (request.json.get("Name"), request.json.get("Email"), request.json.get("Password"), "Tutor",
                   request.json.get("TimeZone")))

    mysql.connection.commit()
    cur.execute("select id from user where Email='" + request.json["Email"] + "' and Password='" + request.json[
        "Password"] + "'")
    rows = cur.fetchall()
    id = rows[0][0]
    return str(id), 200


@courses.route("/api/match", methods=["post"])
def match():
    if not (request.json and request.json.get("sid") and request.json.get("cid")):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("select t.id,s.id,t.name,s.day,s.time,s.id from user t inner join schedule s on t.id=s.uid"
                " inner join allocation a on a.cid=%s "
                # "left outer join enroll e on e.cid=a.cid and e.sid=%s"
                " where s.day in (select day from schedule where uid=%s)"
                " and s.time in(select time from schedule where uid=%s) "
                " and t.role='Tutor' and s.status=0 order by t.name",
                (request.json.get("cid"), request.json.get("sid"), request.json.get("sid")))
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


@courses.route("/api/sendRequest", methods=["Post"])
def sendRequest():
    # todo change this
    if not (request.json and request.json.get('id') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("insert into request(sid,cid) values(%s,%s)", (request.json.get('id'), request.json.get('cid')))

    mysql.connection.commit()

    return 'Successful', 200


@courses.route("/api/showRequest", methods=["post"])
def showRequests():
    if not (request.json and request.json.get("id") and request.json.get("type")):
        return "error", 201
    cur = mysql.connection.cursor()
    if (request.json.get("type") == "admin"):
        cur.execute("select c.*,s.* from request r inner join user s on s.id=r.sid "
                    "inner join courses c on c.id=r.cid")
    else:
        cur.execute("select c.* from request r inner join students s on s.uid=r.sid "
                    "inner join courses c on c.id=r.cid  where r.sid=%s", (request.json.get("id"),))

    rows = cur.fetchall()
    i = 0
    data = {i: rows[i] for i in range(len(rows))}
    cur.close()
    return jsonify(data)


@courses.route("/api/acceptRequest", methods=["post"])
def acceptRequest():
    if not (request.json and request.json.get('sid') and request.json.get('cid') and request.json.get(
            'tid') and request.json.get('schedule_id')):
        return "Error", 201
    cur = mysql.connection.cursor()
    try:
        cur.execute("insert into enroll(sid,cid,tid,schedule_id) values(%s,%s,%s,%s)", (
            request.json.get('sid'), request.json.get('cid'), request.json.get('tid'), request.json.get('schedule_id')))

        mysql.connection.commit()

        cur.execute("insert into resume values(%s,%s,%s,null,null,null)", (
            request.json.get('sid'), request.json.get('tid'), request.json.get('cid')))

        mysql.connection.commit()
    except Exception as e:
        return str(e.__str__()), 201
    try:
        cur.execute("Delete from request where sid=%s and cid=%s",
                    (request.json.get('sid'), request.json.get('cid')))

        mysql.connection.commit()
    except Exception as e:
        return str(e.__str__()), 201
    try:
        cur.execute("select day,time from schedule  where uid=%s and id=%s",
                    (request.json.get('tid'), request.json.get('schedule_id')))
        row = cur.fetchall()
        day, time = row[0][0], row[0][1]
        cur.execute("update schedule set status=1 where day= %s and time=%s and uid=%s",
                    (day, time, request.json.get("sid")))
        mysql.connection.commit()

        cur.execute("update schedule set status=1 where uid=%s and id=%s",
                    (request.json.get('tid'), request.json.get('schedule_id')))

        mysql.connection.commit()
    except Exception as e:
        return str(e.__str__()), 201
    cur.close()
    return 'Successful'


@courses.route("/api/rejectRequest", methods=["post"])
def rejectRequest():
    if not (request.json and request.json.get('sid') and request.json.get('cid')):
        return "Error", 201
    cur = mysql.connection.cursor()
    try:
        cur.execute("Delete from request where sid=%s and cid=%s",
                    (request.json.get('sid'), request.json.get('cid')))
        mysql.connection.commit()
    except Exception as e:
        return "Error", 201
    cur.close()
    return 'Successful'


@courses.route("/api/showEnrolledCourses", methods=["post"])
def showEnrolledCourses():
    if not (request.json and request.json.get("id") and request.json.get("type")):
        return "error", 201
    cur = mysql.connection.cursor()
    if (str(request.json.get("type")).lower() == "tutor"):
        cur.execute("select c.Title,sc.Day,sc.Time,sc.id,e.sid,c.id,u.name from enroll e inner join courses c on "
                    "c.id=e.cid inner join schedule sc "
                    "on sc.id=e.schedule_id inner join user u on u.id=e.sid where  e.tid=%s", (request.json.get('id'),))
    else:
        cur.execute("select c.Title,sc.Day,sc.Time,sc.id,e.tid ,c.id from enroll e inner join courses c on "
                    "c.id=e.cid inner join schedule sc "
                    "on sc.id=e.schedule_id  where  e.sid=%s", (request.json.get('id'),))

    rows = cur.fetchall()
    i = 0
    data = {i: rows[i] for i in range(len(rows))}
    cur.close()
    return jsonify(data)

