from flask import Flask, request, render_template, session
import requests, base64, sqlite3, datetime

app = Flask(__name__)

conn = sqlite3.connect("edubd.db")
cursor = conn.cursor()

host = 'judge0-ce.p.rapidapi.com'
sent_adress = 'https://' + host + '/submissions/'
tok_n = '1806363f0fmshf3926631702e101p1eda9ajsn5e10975d9be7'

heads = {
    'Content-type': 'application/json',
    'X-RapidAPI-Key': tok_n,
    'X-RapidApi-Host': host
}
langes = [{'id': 52, 'name': 'C++ (GCC 7.4.0)'}, {'id': 54, 'name': 'C++ (GCC 9.2.0)'}, {'id': 62, 'name': 'Java (OpenJDK 13.0.1)'}, {'id': 71, 'name': 'Python (3.8.1)'}]
app.secret_key = '1806363f0fmshf3926631702e101p1eda9ajsn5e10975d9be7'

@app.route('/login', methods =['GET', 'POST'])
def login():
    #после отправки формы
    if request.method == 'POST':
        #если не войдено
        if 'username' not in session:
            username = request.form['username']
            cursor.execute("SELECT * FROM users_table_1 WHERE username=?", (username,))
            #если это имя есть в таблице пользователей
            if cursor.fetchone():
                session['username'] = username
                cursor.execute("SELECT role FROM users_table_1 WHERE username=?", (session['username'],))
                session['role'] = cursor.fetchone()
                return render_template('login.html', deta = 'Hello, ' + request.form['username'], role = session['role'], logInfo = 'Logout', title="Login")
            else:
                return render_template('login.html', deta = 'You are not registered', title="Login")
        else:
            return render_template('login.html', deta = 'You are already in as ' + session['username'], logInfo = 'Logout', title="Login")
    else:
        return render_template('login.html', title="Login")

@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'username' not in session:
            session['username'] = request.form['username']
            username = session['username']
            email = request.form['email']
            role = request.form['role']
            cursor.execute("SELECT * FROM users_table_1")
            noun = 0
            f = cursor.fetchone()
            while f:
                noun+=1
                f = cursor.fetchone()
            user_id = noun + 1
            cursor.execute("INSERT OR REPLACE INTO users_table_1(user_id, username, role, email) VALUES (?, ?, ?, ?)", (user_id, username, role, email))
            conn.commit()
            f = cursor.execute("SELECT * FROM users_table_1")
            for i in f:
                print(i)
            print()
            return render_template('register.html', deta = 'Hello, ' + request.form['username'], role = session['role'], logInfo = 'Logout', title="Register")
        else:
            return render_template('register.html', deta = 'You are already in as ' + session['username'], role = session['role'], logInfo = 'Logout', title="Register")
    return render_template('register.html', logInfo = 'Register', title="Register")

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        myCode = request.form.get('qwerty')
        mC = myCode.encode("UTF-8")
        Code = base64.b64encode(mC)
        Cd = Code.decode("UTF-8")
        myCodeLanguage = request.form.get('language')
        myCin = request.form.get('in')
        #Cd = base64.b64decode(myCode)
        dats = {
            "language_id": myCodeLanguage,
            "source_code": Cd,
            "stdin": "SnVkZ2Uw",
            "expected_output": ""
        }
        resp = requests.request("POST", sent_adress, headers = heads, json = dats, params = {"base64_encoded": "true"}).json()
        print(resp)
        #return render_template("sent.html", rets = resp)
        decision_tok_n = resp['token']
        answer = requests.request("GET", sent_adress + decision_tok_n, headers = heads, params = {"base64_encoded": "true"}).json()
        print(answer['status'], " ", answer['stdout'])
        rets = answer['compile_output']
        if rets is None:
            if answer['stdout'] is None:
                rs = "None"
            else:
                rts = base64.b64decode(answer['stdout'].encode("UTF-8"))
                rs = rts.decode("UTF-8")
        #    return render_template("sent.html", langs = langes, rets = "None")
        else:
            rts = base64.b64decode(rets.encode("UTF-8"))
            rs = rts.decode("UTF-8")

        """inserting time of submission"""
        now = datetime.datetime.now()
        time = now.strftime("%H:%M:%S")
        day = now.strftime("%d/%m/%y")

        cursor.execute("INSERT OR REPLACE INTO table572(des_token, lang, code, input, output, time, day) VALUES (?, ?, ?, ?, ?, ?, ?)", (decision_tok_n, myCodeLanguage, myCode, myCin, rs, time, day))
        conn.commit()
        noun = 0
        #cursor.execute("SELECT * FROM table572")
        f = cursor.fetchone()
        while f:
            noun+=1
            f = cursor.fetchone()
            print(f)
        print("You tried to submit this task", noun, "times")
        #cursor.execute("SELECT ")
        return render_template("task1.html", langs = langes, rets = rs, title = "Задание 1")
    else:
        q = 1
        langs = []
        for i in langes:
            langs.append(i['name'])
            q = q + 1
        return render_template("task1.html", langs = langes, title = "Задание 1")#, langs = langs)

if __name__ == '__main__':
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_table_1
    (user_id UNIQUE, username, mail, password, role)
    """)
    conn.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks
    (task_id UNIQUE, task_text, author, tests, exp_output)
    """)
    conn.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS solutions
    (sol_id UNIQUE, lang, code, input, time_of_sol, day_of_sol)
    """)
    conn.commit()

    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
