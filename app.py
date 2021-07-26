from flask import render_template, url_for, request, session, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import app, db
from methods import send_email, password_checker
from lecturer import lecturer


@app.route('/')
@app.route('/home')
def index():
    if 'username' in session:
        return render_template('home.html')
    else:
        return redirect('login')


@app.route('/about')
def about():
    if 'username' in session:
        return render_template('about.html')
    else:
        return redirect('login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    name = 'login.html'
    if request.method == "POST":

        if '@' not in request.form['email']:
            return render_template(name, error='Неправильно введена почта!')

        elif not request.form['email']:
            return render_template(name, error='Поле для почты пустое!')

        elif not request.form['password']:
            return render_template(name, error='Поле для пароля пустое!')

        if db["stuff"].count_documents({'Почта': request.form['email']}) == 1:

            password = db["stuff"].find_one({'Почта': request.form['email']})['Пароль']
            if check_password_hash(password, request.form['password']):

                session['username'] = db["stuff"].find_one({'Почта': request.form['email']})['Фамилия и имя']
                session['role'] = db["stuff"].find_one({'Почта': request.form['email']})['Роль']
                flash(f'Добро пожаловать в систему,{session["username"]}')
                return redirect('home')

            else:
                return render_template(name, error='Неправильный пароль!')

        else:
            error = '''Почты нет в БД.  
                    Пройдите регистрацию!'''

    return render_template('login.html', error=error)


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    name = 'register.html'
    if request.method == "POST":
        if '@' not in request.form['email']:
            return render_template(name, error='Неправильно введена почта!')

        elif not request.form['email']:
            return render_template(name, error='Поле для почты пустое!')

        elif not request.form['password']:
            return render_template(name, error='Поле для пароля пустое!')

        elif request.form['password'] != request.form['password2']:
            return render_template(name, error='Пароли не совпадают!')

        elif not password_checker(request.form['password']):
            return render_template(name, error='Пароль ненадежный!')

        elif request.form['group'] == 'Преподаватель' and request.form['full_name'] not in lecturer:
            error = """Данного преподавателя нет в списке, 
                        регистрация невозможна! """
            return render_template(name, error=error)

        elif not request.form['full_name'] or not request.form['patronymic']:
            return render_template(name, error='Не все поля были заполнены!')

        elif db["stuff"].count_documents({'Почта': request.form['email']}) != 0:
            return render_template(name, error='С данной почтой уже есть аккаунт!')

        else:
            info = {}
            info["Почта"] = request.form['email']
            info["Фамилия и имя"] = request.form['full_name']
            info["Отчество"] = request.form['patronymic']
            info["Пароль"] = generate_password_hash(request.form['password'])
            if request.form['group'] == 'Преподаватель':
                info["Роль"] = request.form['group']
            else:
                info["Роль"] = 'Студент'
                info['Группа'] = request.form['group']
            db["stuff"].insert_one(info)

            session['username'] = request.form['full_name']
            session['role'] = request.form['group']
            flash(f'Добро пожаловать в систему,{session["username"]}')
            return redirect('home')

    return render_template(name, error=error)


@app.route('/teachers', methods=['POST', 'GET'])
def teachers():
    if session['role'] == 'Преподаватель':
        if request.method == "POST":
            auth_info = {}
            auth_info['author'] = session['username']
            auth_info['title'] = request.form['title']
            auth_info['description'] = request.form['description']
            group = request.form['group']

            if group != 'Расслыка студентам' or group != 'Расслыка преподавателям':
                students_list = db["stuff"].find({'Группа': group})
                for student in students_list:
                    send_email(auth_info, student)

            if group == 'Расслыка студентам':
                members = db["stuff"].find({"Роль": 'Студент'})
                for student in members:
                    send_email(auth_info, student)

            if group == 'Расслыка преподавателям':
                members = db["stuff"].find({"Роль": 'Преподаватель'})
                for member in members:
                    send_email(auth_info, member)

            return redirect('home')

        return render_template('teachers.html')

    flash(f'У вас недостаточно прав,{session["username"]}')
    return redirect('home')


if __name__ == '__main__':
    app.run(debug=True)