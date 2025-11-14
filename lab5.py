from flask import Flask, Blueprint, render_template, request, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Добавьте секретный ключ для сессий

# Создаем Blueprint для lab5
lab5 = Blueprint('lab5', __name__, template_folder='templates', static_folder='static')

@lab5.route('/lab5/')
def index():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    # Используем правильное имя базы данных
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='arina_neyvert_knowledge_base',  # Исправлено с 'kb' на правильное имя
        user='arina_neyvert_knowledge_base',
        password='1967'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab5.route('/lab5/list')
def list_articles():
    return "Список статей"

@lab5.route('/lab5/create')
def create_article():
    return "Создать статью"

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/register.html', error='Заполните все поля')
    
    # Используем функцию db_connect вместо прямого подключения
    conn, cur = db_connect()

    # Используем параметризованные запросы для безопасности
    cur.execute("SELECT login FROM users WHERE login = %s;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html',
                               error="Такой пользователь уже существует")
    
    password_hash = generate_password_hash(password)
    # Используем параметризованные запросы
    cur.execute("INSERT INTO users (login, password) VALUES (%s, %s);", 
                (login, password_hash))
    
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
    
    # Используем функцию db_connect вместо прямого подключения
    conn, cur = db_connect()

    # Используем параметризованные запросы
    cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
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