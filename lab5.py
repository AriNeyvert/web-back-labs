from flask import Flask, Blueprint, render_template, request, session
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Создаем Blueprint для lab5
lab5 = Blueprint('lab5', __name__, template_folder='templates', static_folder='static')

@lab5.route('/lab5/')
def index():
    return render_template('lab5/lab5.html', login=session.get('login'))

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
    
    conn=psycopg2.connect(
        host = '127.0.0.1',
        database = 'arina_neyvert_knowledge_base',
        user = 'arina_neyvert_knowledge_base',
        password = '1967'
    )
    cur = conn.cursor()

    cur.execute(f"SELECT login FROM users WHERE login='{login}';")
    if cur.fetchone():
        cur.close()
        conn.close()
        return render_template('lab5/register.html',
                               error="Такой пользователь уже существует")
    cur.execute(f"INSERT INTO users (login, password) VALUES ('{login}', '{password}');")
    conn.commit()
    cur.close()
    conn.close()
    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not (login and password):
        return render_template('lab5/login.html', error="Заполните все поля")
    
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='arina_neyvert_knowledge_base',
        user='arina_neyvert_knowledge_base',
        password='1967'
    )
    cur = conn.cursor(cursor_factory = RealDictCursor)

    cur.execute(f"SELECT * FROM users WHERE login='{login}';")
    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    if user['password'] != password:
        cur.close()
        conn.close()
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    session['login'] = login
    cur.close()
    conn.close()
    return render_template('lab5/success_login.html', login=login)
