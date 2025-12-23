from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from flask_login import login_user, logout_user, login_required, current_user
from flask_login import LoginManager
from datetime import datetime

lab8 = Blueprint('lab8', __name__, 
                 template_folder='templates/lab8',
                 static_folder='static/lab8')

@lab8.route('/lab8/')
@lab8.route('/index')
def index():
    # Если пользователь авторизован через Flask-Login, используем его данные
    if current_user.is_authenticated:
        username = current_user.login
    else:
        username = session.get('login', 'anonymous')
    
    # Получаем статьи текущего пользователя
    user_articles = []
    if current_user.is_authenticated:
        user_articles = articles.query.filter_by(login_id=current_user.id).all()
    
    return render_template('lab8/index.html', 
                          username=username, 
                          user_articles=user_articles)

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
                               login=login_form)
    
    if not password_form or not password_form.strip():
        return render_template('lab8/register.html',
                               error='Пароль не может быть пустым',
                               login=login_form)
    
    # Проверяем, существует ли пользователь с таким логином
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                               error='Такой пользователь уже существует',
                               login=login_form)
    
    # Хешируем пароль и создаем нового пользователя
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматически логиним пользователя после регистрации
    remember = request.form.get('remember') == 'on'
    login_user(new_user, remember=remember)
    session['login'] = login_form
    return redirect('/lab8/')

@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember') == 'on'  # Получаем значение галочки "запомнить меня"
    
    # Проверка на пустые значения для формы входа
    if not login_form or not login_form.strip():
        return render_template('lab8/login.html',
                               error='Логин не может быть пустым',
                               login=login_form)
    
    if not password_form or not password_form.strip():
        return render_template('lab8/login.html',
                               error='Пароль не может быть пустым',
                               login=login_form)

    user = users.query.filter_by(login=login_form).first()
    
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember)
            session['login'] = login_form
            return redirect('/lab8/')
    
    return render_template('lab8/login.html',
                           error='Ошибка входа: логин и/или пароль неверны',
                           login=login_form)

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    session.pop('login', None)  # Удаляем логин из сессии
    return redirect('/lab8/')

@lab8.route('/lab8/articles/')
@login_required
def article_list():
    # Получаем все статьи текущего пользователя
    user_articles = articles.query.filter_by(login_id=current_user.id).all()
    return render_template('lab8/articles.html', articles=user_articles)

@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not title.strip():
        return render_template('lab8/create.html',
                               error='Заголовок не может быть пустым',
                               title=title,
                               content=content)
    
    if not content or not content.strip():
        return render_template('lab8/create.html',
                               error='Содержание статьи не может быть пустым',
                               title=title,
                               content=content)
    
    # Создаем новую статью (убрано created_at из параметров)
    new_article = articles(
        title=title,
        article_text=content,
        login_id=current_user.id,
        is_public=True
        # created_at заполнится автоматически через default=datetime.utcnow
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles')

@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if not article:
        return redirect('/lab8/articles')
    
    if request.method == 'GET':
        return render_template('lab8/edit.html', article=article)
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not title.strip():
        return render_template('lab8/edit.html',
                               article=article,
                               error='Заголовок не может быть пустым')
    
    if not content or not content.strip():
        return render_template('lab8/edit.html',
                               article=article,
                               error='Содержание статьи не может быть пустым')
    
    # Обновляем статью (убрано обновление created_at)
    article.title = title
    article.article_text = content
    # created_at не обновляем, оно остается оригинальной датой создания
    
    db.session.commit()
    
    return redirect('/lab8/articles')

@lab8.route('/lab8/delete/<int:article_id>', methods=['POST'])
@login_required
def delete(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if article:
        db.session.delete(article)
        db.session.commit()
    
    return redirect('/lab8/articles')
