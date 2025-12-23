from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from flask_login import login_user, logout_user, login_required, current_user

lab8 = Blueprint('lab8', __name__, 
                 template_folder='templates/lab8',
                 static_folder='static/lab8')

@lab8.route('/lab8/')
@lab8.route('/index')
def index():
    username = session.get('login', 'anonymous')
    return render_template('lab8/index.html', username=username)

@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения
    if not login_form or not login_form.strip():
        return render_template('lab8/register.html',
                               error='Логин не может быть пустым',
                               login=login_form)  # Сохраняем введенный логин
    
    if not password_form or not password_form.strip():
        return render_template('lab8/register.html',
                               error='Пароль не может быть пустым',
                               login=login_form)  # Сохраняем введенный логин
    
    # Проверяем, существует ли пользователь с таким логином
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                               error='Такой пользователь уже существует',
                               login=login_form)  # Сохраняем введенный логин
    
    # Хешируем пароль и создаем нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматически логиним пользователя после регистрации
    login_user(new_user, remember=False)
    session['login'] = login_form
    return redirect('/lab8/')

@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения для формы входа
    if not login_form or not login_form.strip():
        return render_template('lab8/login.html',
                               error='Логин не может быть пустым',
                               login=login_form)  # Сохраняем введенный логин
    
    if not password_form or not password_form.strip():
        return render_template('lab8/login.html',
                               error='Пароль не может быть пустым',
                               login=login_form)  # Сохраняем введенный логин

    user = users.query.filter_by(login=login_form).first()
    
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=False)
            session['login'] = login_form
            return redirect('/lab8/')
    
    return render_template('lab8/login.html',
                           error='Ошибка входа: логин и/или пароль неверны',
                           login=login_form)  # Сохраняем введенный логин

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    session.pop('login', None)  # Удаляем логин из сессии
    return redirect('/lab8/')

@lab8.route('/lab8/articles/')
@login_required
def article_list():
    return "cписок статей"

@lab8.route('/create')
def create():
    return "Создание статьи (заготовка)"