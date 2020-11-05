from flask import Flask
from flask import jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'ProjectDb'
mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("select * from user")
    rv = cur.fetchall()
    table = "<table border='1'><tr><th>ID</th><th>Name</th><th>Age</th><th>City</th></tr>"
    for row in rv:
        table += ("<tr><td>" + str(row[0]) + "</td><td>" \
                  + row[1] + "</td><td>" + str(row[2]) + "</td><td>" \
                  + row[3] + "</td></tr>")

    table += ("</table>")

    return table


list_of_users = []


@app.route('/api/users', methods=['GET'])
def api_user():
    cur = mysql.connection.cursor()
    cur.execute("select * from users")
    rv = cur.fetchall()
    list_of_users = []
    for row in rv:
        data = {}
        data['ID'] = row[0]
        data['Name'] = row[1]
        data['Age'] = row[2]
        data['City'] = row[3]
        list_of_users.append(data)
    cur.close()
    return jsonify(list_of_users)


@app.route("/api/user", methods=['Post'])
def append_user():
    if not (request.json and request.json["Name"] and request.json["Age"] and request.json["City"]):
        return "Error"

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Users(Name, Age,City) VALUES (%s, %s,%s)" \
                , (request.json.get("Name"), int(request.json.get("Age")), request.json.get("City")))
    mysql.connection.commit()
    cur.close()

    return "successful"


@app.route("/api/chkstudent", methods=['Post'])
def chkStudent():
    if not (request.json and request.json["Email"] and request.json["Password"]):
        return "Error"
    cur = mysql.connection.cursor()
    cur.execute("select * from students where Email='" + request.json["Email"] + "' and Password='" + request.json[
        "Password"] + "'")
    res = cur.fetchall()
    if (res != ()):
        return str(res[0][0])
    return "error"


@app.route("/api/students", methods=['Post'])
def add_student():
    if not (request.json and request.json["Email"] and request.json["Password"]):
        return "Error"

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Students(Name,Email,Password,Cnic) VALUES (%s, %s,%s,%s)" \
                , (request.json.get("Name"), request.json.get("Email"), request.json.get("Password"),
                   request.json.get("Cnic")))
    mysql.connection.commit()
    cur.close()

    return "successful"


@app.route("/api/schedule", methods=['Post'])
def schedule():
    cur = mysql.connection.cursor()
    if not (request.json and request.json["Day"] and request.json["Time"]):
        return "Error"
    cur.execute( "Select * from schedule where sid=%s and chkId=%s",(int(request.json.get("ID")),int(request.json.get("chkId"))))
    res=cur.fetchall()
    if (len(res)>0):
        cur.execute("Delete from schedule where sid=%s and chkId=%s",(int(request.json.get("ID")), int(request.json.get("chkId"))))
    else:
        cur.execute("INSERT INTO Schedule(sid,Day,Time,chkId) VALUES (%s,%s, %s,%s)" \
                    , (int(request.json.get("ID")), request.json.get("Day"), request.json.get("Time"),
                       int(request.json.get("chkId"))))

    mysql.connection.commit()
    cur.close()
    return str(res)


@app.route("/api/readSchedule", methods=['Post'])
def readSchedule():
    id=int(request.json.get("ID"))
    if not id:
        return  "Error empty id"
    cur = mysql.connection.cursor()
    cur.execute("Select chkId from schedule where sid=%s",(id,))
    lst=[]
    for row in cur:
        lst.append(row[0])
    return jsonify(lst)

def chkData(query):
    cur = mysql.connection.cursor()
    cur.execute(query)

    res = cur.fetchall()
    cur.close()
    if (res != ()):
        return True
    return False



if __name__ == '__main__':
    app.run()
