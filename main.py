from flask import Flask, render_template, redirect, session, request
import sqlite3
import time
from tempfile import mkdtemp


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"


@app.route('/setup')
def setup():
    conn = sqlite3.connect("chatbox.db", check_same_thread=False)
    sql = '''CREATE TABLE IF NOT EXISTS tbl_chats(id INTEGER NOT NULL PRIMARY KEY,
        ts INTEGER NOT NULL,
        chat VARCHAR(255) NOT NULL
        );'''
    conn.execute(sql)
    try:
        sql = '''INSERT INTO tbl_chats (id,ts,chat) VALUES(0,0,"Welcome");'''
        conn.execute(sql)
        conn.commit()
        conn.close()
    except:
        return "that didn't work, you probably already have this data"
    return redirect("/")


@app.route('/', methods=['POST', 'GET'])
def index():
    next_id = 0
    if "end" not in session:
        session["end"] = 0
    if "limit" not in session:
        session["limit"] = 0

    try:
        # get number of current post
        conn = sqlite3.connect("chatbox.db", check_same_thread=False)
        sql = "SELECT COUNT(id) FROM tbl_chats;"
        data = conn.execute(sql)

        for row in data:
            count = int(row[0])
        

        # hold the most recent 20 post
        sql = "SELECT MAX(id) FROM tbl_chats;"
        data = conn.execute(sql)

        for row in data:
            next_id = int(row[0]) + 1
        conn.close()

        session["end"] = count

    except:
        return "The count heck the count did not work!"

    # get the id of the most recent addition to db
    nav = count-1
    if request.method == 'GET':
        nav = request.args.get('nav')
        if nav is None:
            session['limit'] = count-1
        else:
            nav = int(nav)
            if nav > count - 1:
                session['limit'] = count - 1
            elif nav < 0:
                session['limit'] = 0
            else:
                session['limit'] = nav

    conn = sqlite3.connect("chatbox.db")
    sql = "SELECT id, ts, chat FROM tbl_chats ORDER BY ts DESC;"

    data = conn.execute(sql)
    display = []
    try:
        for row in data:
            display.append(str(row[0]) + ' - ' + str(row[2]))
    except:
        return "have you tried /setup?"
    conn.close()

    # if post detected, get the post and add it to database
    if request.method == 'POST':
        ts = time.time()
        chat = request.form.get("chat")
        sql = "INSERT INTO tbl_chats (id,ts,chat) VALUES("+str(next_id)+","+str(ts)+",'"+chat+"');"
        conn = sqlite3.connect("chatbox.db", check_same_thread=False, timeout=10)
        conn.execute(sql)
        conn.commit()
        conn.close()
        # then, redirect to this route
        return redirect("/")
    # else get all the chats database and display the most recent 20

    # return render_template("index.html", display=display, limit=limit, last=next_id, current=chat_range)
    return render_template("index.html", display=display, lastpost=session['end'], limit=session['limit'])

@app.route('/search', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        q = request.form.get("q")
        q = "%"+q+"%"
        sql = ("""SELECT * FROM tbl_chats WHERE chat like '%s';""" %(q,))
        conn = sqlite3.connect("chatbox.db")
        data = conn.execute(sql)
        display = []
        try:
            for row in data:
                display.append(str(row[0]) + ' - ' + str(row[2]))
        except:
            return "have you tried /setup?"
        conn.close()
        return render_template("search.html", display=display)
    if request.method != 'POST':
        return render_template("search.html", display=[])


if __name__ == '__main__':
    app.run()