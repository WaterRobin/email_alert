from flask import Flask, render_template, url_for, request, session, redirect,flash
from pymongo import MongoClient

import datetime
import smtplib

app = Flask(__name__)
app.config['SECRET_KEY'] = '320213829f2b99c5a69ab1bbc32d8826f7cb183b'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=10)

cluster = MongoClient("mongodb+srv://Robin:aBkea7qLvgNnGJeA@cluster0.an4ea.mongodb.net/gena?retryWrites=true&w=majority")
db = cluster["gena"]

lecturer = {
    "Илья Бондарев": 'password',
    "Даниил Меркулов": 'superpassword'
}


def send_email(auth_inf, db_object):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('tstmiigaik@gmail.com', 'testpassword_01')
    to_email = db_object['Почта']
    msg = f"""
    Письмо от {auth_inf['author']} для {db_object['Фамилия']} {db_object['Имя']} {db_object['Отчество']}
    Тема: {auth_inf['title']}.

    {auth_inf['description']}
    
    Спасибо за внимание.
    """.encode('utf-8')
    s.sendmail("tstmiigaik@gmail.com", to_email, msg)
    s.quit()


@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/students', methods=['POST', 'GET'])
def students():
    if request.method == "POST":
        if db["stuff"].find({'Почта': request.form['email']}) == 0:
            db["stuff"].insert_one({
                'Почта': request.form['email'],
                'Фамилия': request.form['second_name'],
                'Имя': request.form['first_name'],
                'Отчество': request.form['patronymic'],
                'Группа': request.form['group']
            })
            return redirect('home')

        return render_template('students.html')

    else:
        return render_template('students.html')


@app.route('/teachers', methods=['POST', 'GET'])
def teachers():
    if 'username' in session:
        if request.method == "POST":
            auth_info = {}
            auth_info['author'] = session['username']
            auth_info['title'] = request.form['title']
            auth_info['description'] = request.form['description']
            group = request.form['group']
            students_list = db["stuff"].find({'Группа': group})

            for student in students_list:
                send_email(auth_info, student)

            return redirect('home')

        return render_template('teachers.html')

    return redirect('teachers_login')


@app.route('/teachers_login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in lecturer and lecturer[request.form['username']] == request.form['password']:
            session["username"] = request.form['username']
            session.modified = True
        return redirect('teachers')
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)