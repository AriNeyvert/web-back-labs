from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash
from db import db
from db.models import users, articles

lab8 = Blueprint('lab8', __name__, 
                 template_folder='templates/lab8',
                 static_folder='static/lab8')

@lab8.route('/lab8/')
@lab8.route('/index')
def index():
    return render_template('lab8/index.html', username="anonymous")

@lab8.route('/login')
def login():
    return "Страница входа (заготовка)"

@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    # Проверка на пустые значения
    if not login_form or not login_form.strip():
        return render_template('lab8/register.html',
                               error='Логин не может быть пустым')
    
    if not password_form or not password_form.strip():
        return render_template('lab8/register.html',
                               error='Пароль не может быть пустым')
    
    # Проверяем, существует ли пользователь с таким логином
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                               error='Такой пользователь уже существует',
                               request=request)  # Передаем request для сохранения введенного логина
    
    # Хешируем пароль и создаем нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/lab8/')

@lab8.route('/articles')
def articles():
    return "Список статей (заготовка)"

@lab8.route('/create')
def create():
    return "Создание статьи (заготовка)"