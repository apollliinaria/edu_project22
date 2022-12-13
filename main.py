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

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template("login.html", title = "Login")
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        myCode = request.form.get('code_area')
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
