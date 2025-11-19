from flask import Flask, Blueprint, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
# Добавляем конфигурацию для типа базы данных
app.config['DB_TYPE'] = 'sqlite'  # или 'postgres'

# Создаем Blueprint для lab5
lab5 = Blueprint('lab5', __name__, template_folder='templates', static_folder='static')

@lab5.route('/lab5/')
def index():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':  # ИСПРАВЛЕНИЕ: postgres вместо postres
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='arina_neyvert_knowledge_base',
            user='arina_neyvert_knowledge_base',
            password='1967'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()    
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

def execute_query(cur, query, params):
    """Универсальная функция для выполнения запросов с учетом типа БД"""
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(query, params)
    else:
        # Заменяем %s на ? для SQLite
        query = query.replace('%s', '?')
        cur.execute(query, params)

@lab5.route('/lab5/list')
def list_articles():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    conn, cur = db_connect()

    execute_query(cur, "SELECT id FROM users WHERE login = %s;", (login,))
    user = cur.fetchone()
    
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')
    
    user_id = user['id']

    execute_query(cur, "SELECT * FROM articles WHERE user_id = %s;", (user_id,))
    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('lab5/articles.html', articles=articles, login=login)

@lab5.route('/lab5/create', methods=['GET', 'POST'])
def create_article():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')

    if not (title and article_text):
        return render_template('lab5/create_article.html', error='Заполните все поля')

    conn, cur = db_connect()

    # Получаем id пользователя
    execute_query(cur, "SELECT id FROM users WHERE login = %s;", (login,))
    user = cur.fetchone()
    
    if not user:
        db_close(conn, cur)
        return render_template('lab5/create_article.html', error='Пользователь не найден')
    
    user_id = user['id']

    execute_query(cur, "INSERT INTO articles (user_id, title, article_text) VALUES (%s, %s, %s);", 
                (user_id, title, article_text))
    
    db_close(conn, cur)
    return redirect('/lab5/')

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/register.html', error='Заполните все поля')
    
    conn, cur = db_connect()

    execute_query(cur, "SELECT login FROM users WHERE login = %s;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error="Такой пользователь уже существует")
    
    password_hash = generate_password_hash(password)

    execute_query(cur, "INSERT INTO users (login, password) VALUES (%s, %s);", (login, password_hash))
    
    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/login.html', error="Заполните все поля")
    
    conn, cur = db_connect()

    execute_query(cur, "SELECT * FROM users WHERE login = %s;", (login,))
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)

# Добавляем обработчик для выхода
@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab5/')

# Обработчик для favicon.ico
@lab5.route('/favicon.ico')
def favicon():
    return '', 404

# Регистрируем blueprint
app.register_blueprint(lab5)

if __name__ == '__main__':
    app.run(debug=True)