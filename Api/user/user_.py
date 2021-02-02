from flask import render_template
from flask import jsonify, request, Response

from Api import  mysql
from . import user

@user.route('/')
def sessions():
    return render_template('session.html')

# @app.route('/api/users', methods=['GET'])
# def api_user():
#     cur = mysql.connection.cursor()
#     cur.execute("select * from users")
#     rv = cur.fetchall()
#     list_of_users = []
#     for row in rv:
#         data = {}
#         data['ID'] = row[0]
#         data['Name'] = row[1]
#         data['Age'] = row[2]
#         data['City'] = row[3]
#         list_of_users.append(data)
#     cur.close()
#     return jsonify(list_of_users)


@user.route("/api/chkstudent", methods=['Post'])
def chkStudent():
    if not (request.json and request.json.get("Email") and request.json.get("Password")):
        return "Error", 201
    cur = mysql.connection.cursor()
    cur.execute("select * from user where Email='" + request.json["Email"] + "' and Password='" + request.json[
        "Password"] + "'")
    rows = cur.fetchall()
    data = {}
    try:
        data['id'] = rows[0][0]
        data['name'] = rows[0][1]
        data['email'] = rows[0][2]
        data['password'] = rows[0][3]
        data['role'] = rows[0][4]
    except Exception as e:
        return str(e),201
    return jsonify(data)

@user.route("/api/returnCnic", methods=['Post'])
def returnCnic():
    if not (request.json and request.json.get("id")):
        return "Error", 201
    cur = mysql.connection.cursor()
    rows=None
    try:
        cur.execute("select FatherCnic from Parents where uid=" + str(request.json["id"]))

        rows = cur.fetchall()
    except Exception as e:
        print(e.__str__())
        return "error",201

    return jsonify(rows[0][0])

@user.route("/api/add_parent", methods=['Post'])
def add_parent():
    if not (request.json and request.json.get("Email") and request.json.get("Password") and request.json.get("Cnic")):
        return "Error"

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO User(Name,Email,Password,Role,TimeZone) VALUES (%s,%s,%s,%s,%s)" \
                , (request.json.get("Name"), request.json.get("Email"), request.json.get("Password"), "Parent",
                   request.json.get("TimeZone")))
    mysql.connection.commit()
    id = returnId(request.json.get("Email"), request.json.get("Password"))
    if (id == None):
        return jsonify("Error"), 201

    cur.execute("INSERT INTO parents(uid,FatherCNIC) VALUES (%s,%s)", ( \
        int(id), request.json.get("Cnic")))
    mysql.connection.commit()
    cur.close()
    return "successful", 200

@user.route("/api/addStudent", methods=['Post'])
def add_student():
    if not (request.json and request.json.get("Name") and request.json.get("Password")):
        return "Error"
    from datetime import datetime
    stamp=datetime.now().timestamp()
    append=hex(int(stamp)).split('x')[1]
    username=request.json["Name"].split(' ')[0]+append
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO User(Name,Email,Password,Role,TimeZone) VALUES (%s,%s,%s,%s,%s)" \
                    , (request.json.get("Name"), username, request.json.get("Password"), "Student",
                       request.json.get("TimeZone")))
        uid = returnId(username, request.json.get("Password"))
        cnic=str(request.json.get("cnic")).replace(" ","")
        cur.execute("select id from parents where uid=%s", ( \
            request.json.get("uid"),))
        rows = cur.fetchall()

        pid = rows[0][0]

        cur.execute("insert into students values(%s,%s)", (uid, pid))
        mysql.connection.commit()
    except Exception as e:
        print(e.__str__())
        return "error",201
    cur.close()

    return "successful", 200

@user.route("/api/getStudents", methods=["post"])
def getStudents():
    if not (request.json):
        return "Error", 201

    cur = mysql.connection.cursor()
    if (str(request.json.get("role")).lower() == "parent"):
        cur.execute("Select u.* from user u inner join students s on s.uid=u.id  "
                    "where s.pid=(select pid from parents where uid=%s)",
                    (request.json.get('id'),))
    elif (request.json.get("role") == "tutor"):
        cur.execute("Select c.* from courses c where id not in (select cid from allocation where tid=%s)"
                    " and id not in (select cid from enroll where tid=%s)",
                    (request.json.get('id'), request.json.get('id')))

    rows = cur.fetchall()
    data = {row[0]:[row[1],row[2],row[3]] for row in rows}

    return jsonify(data)

@user.route("/api/schedule", methods=['Post'])
def schedule():
    cur = mysql.connection.cursor()
    if not (request.json and request.json.get("Day") and request.json.get("Time")):
        return "Error", 201
    cur.execute("Select * from schedule where uid=%s and ChkId=%s",
                (int(request.json.get("ID")), int(request.json.get("chkId"))))
    res = cur.fetchall()
    print(len(res))
    if (len(res) > 0):
        cur.execute("Delete from schedule where uid=%s and chkId=%s",
                    (int(request.json.get("ID")), int(request.json.get("chkId"))))
    else:
        cur.execute("INSERT INTO schedule(uid,Day,Time,ChkId,status) VALUES (%s,%s, %s,%s,%s)" \
                    , (int(request.json.get("ID")), request.json.get("Day"), request.json.get("Time"),
                       int(request.json.get("chkId")), request.json.get("status")))

    mysql.connection.commit()
    cur.close()
    return str(res)


@user.route("/api/readSchedule", methods=['Post'])
def readSchedule():
    if not (request.json and request.json.get("ID")):
        return Response("{'Error':'Empty ID'}", status=201, mimetype='application/json')
    id = 0
    try:
        id = int(request.json.get("ID"))
    except:
        return "ID must be int", 201

    cur = mysql.connection.cursor()
    cur.execute("Select ChkId,status from schedule where uid=%s", (id,))
    lst_ids = []
    lst_status = []
    for row in cur:
        lst_ids.append(row[0])
        lst_status.append(row[1])
    map = {'lst1': lst_ids, "lst2": lst_status}
    return jsonify(map)


def returnId(email, password):
    cur = mysql.connection.cursor()
    cur.execute("Select id from user where email=%s and password =%s",
                (email, password)
                )

    res = cur.fetchall()
    cur.close()

    return str(res[0][0])

