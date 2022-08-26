import os
import sqlite3

from flask import Flask, render_template, request, g, flash, redirect, url_for, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from my_org.data_base import FDataBase
from my_org.forms import LoginForm, RegisterForm
from my_org.user_login import UserLogin
from my_org.config import DATABASE, DEBUG, SECRET_KEY, MAX_CONTENT_LENGTH


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(__name__)
    app.config.update(dict(DATABASE=os.path.join(app.root_path, 'my_org.db')))
    return app


app = create_app()


def login_m():
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
    login_manager.login_message_category = "success"
    return login_manager


login_manager = login_m()


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().from_db(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def create_db():
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('main_page.html', menu=dbase.get_menu())


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.get_user_by_email(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.get_menu(), title="Авторизация", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['psw'])
        res = dbase.add_user(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=dbase.get_menu(), title="Регистрация", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    todo_list = dbase.get_todo_db(current_user.get_id())
    return render_template("profile.html", menu=dbase.get_menu(), title="Профиль", todo_list=todo_list)


@app.route("/userava")
@login_required
def userava():
    img = current_user.get_avatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers["Content-Type"] = "image/png"
    return h


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file and current_user.verify_ext(file.filename):
            try:
                img = file.read()
                res = dbase.update_user_avatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route("/add_task", methods=["POST"])
def add_task():
    if request.method == "POST":
        task_content = request.form["title"]
        dbase.add_todo_db(current_user.get_id(), task_content)
    return redirect(url_for("profile"))


@app.route("/delete_task/<int:todo_id>", methods=["GET"])
def delete_task(todo_id):
    try:
        dbase.del_todo_db(todo_id)
        return redirect(url_for("profile"))
    except:
        return redirect(url_for("profile"))


@app.route('/update_task/<int:todo_id>', methods=["GET"])
def update_task(todo_id):
    dbase.update_todo_db(todo_id)
    return redirect(url_for('profile'))
