from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

rgz = Blueprint('rgz', __name__)

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('cinema.db')
    conn.row_factory = sqlite3.Row
    return conn
# Конфигурация БД
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'cinema_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', '1967'),
        port=os.environ.get('DB_PORT', '5432')
    )
    return conn

# Инициализация БД
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Создание таблицы пользователей
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            login VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы сеансов
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            movie_title VARCHAR(200) NOT NULL,
            session_date DATE NOT NULL,
            session_time TIME NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы бронирований
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            session_id INTEGER REFERENCES sessions(id),
            seat_number INTEGER NOT NULL,
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, seat_number)
        )
    ''')
    
    # Создание администратора по умолчанию
    admin_password = generate_password_hash('admin123')
    cur.execute('''
        INSERT INTO users (name, login, password_hash, is_admin) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (login) DO NOTHING
    ''', ('Администратор', 'admin', admin_password, True))
    
    # Создание тестовых пользователей
    test_users = [
        ('Иван Иванов', 'user1', 'pass1'),
        ('Петр Петров', 'user2', 'pass2'),
        ('Мария Сидорова', 'user3', 'pass3'),
        ('Анна Ковалева', 'user4', 'pass4'),
        ('Сергей Смирнов', 'user5', 'pass5'),
        ('Ольга Орлова', 'user6', 'pass6'),
        ('Дмитрий Волков', 'user7', 'pass7'),
        ('Екатерина Новикова', 'user8', 'pass8'),
        ('Алексей Морозов', 'user9', 'pass9'),
        ('Наталья Павлова', 'user10', 'pass10')
    ]
    
    for name, login, password in test_users:
        password_hash = generate_password_hash(password)
        cur.execute('''
            INSERT INTO users (name, login, password_hash) 
            VALUES (%s, %s, %s)
            ON CONFLICT (login) DO NOTHING
        ''', (name, login, password_hash))
    
    # Создание тестовых сеансов (прошедшие и предстоящие)
    from datetime import date, time
    test_sessions = [
        # Прошедшие сеансы
        ('Аватар: Путь воды', date(2024, 1, 20), time(18, 0)),
        ('Оппенгеймер', date(2024, 1, 21), time(19, 30)),
        ('Барби', date(2024, 1, 22), time(17, 0)),
        # Предстоящие сеансы
        ('Джон Уик 4', date(2025, 1, 23), time(20, 0)),
        ('Человек-паук: Паутина вселенных', date(2025, 1, 24), time(16, 30)),
        ('Дюна: Часть вторая', date(2025, 1, 25), time(19, 0)),
        ('Гладиатор 2', date(2025, 1, 26), time(20, 30))
    ]
    
    for movie, s_date, s_time in test_sessions:
        cur.execute('''
            INSERT INTO sessions (movie_title, session_date, session_time) 
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        ''', (movie, s_date, s_time))
    
    # Создание тестовых бронирований для демонстрации
    test_bookings = [
        (2, 1, 5),   # user1 бронирует место 5 на сеанс 1
        (2, 1, 10),  # user1 бронирует место 10 на сеанс 1
        (3, 1, 15),  # user2 бронирует место 15 на сеанс 1
        (4, 4, 3),   # user3 бронирует место 3 на сеанс 4
        (2, 4, 7),   # user1 бронирует место 7 на сеанс 4
        (3, 4, 12),  # user2 бронирует место 12 на сеанс 4
        (4, 5, 20),  # user3 бронирует место 20 на сеанс 5
        (2, 5, 25)   # user1 бронирует место 25 на сеанс 5
    ]
    
    for user_id, session_id, seat_number in test_bookings:
        try:
            cur.execute('''
                INSERT INTO bookings (user_id, session_id, seat_number) 
                VALUES (%s, %s, %s)
                ON CONFLICT (session_id, seat_number) DO NOTHING
            ''', (user_id, session_id, seat_number))
        except:
            pass  # Игнорируем ошибки если бронирование уже существует
    
    conn.commit()
    cur.close()
    conn.close()

# Валидация логина и пароля
def validate_credentials(login, password):
    import re
    # Проверяем, что содержат только латинские буквы, цифры и некоторые знаки препинания
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]*$'
    return bool(re.match(pattern, login)) and bool(re.match(pattern, password))

# Главная страница РГЗ
@rgz.route('/rgz')
def main():
    if 'user_id' not in session:
        return render_template('rgz/login.html', 
                             student_name="Нейверт Арина Сергеевна",
                             group="ФБИ-33")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем информацию о пользователе
    cur.execute('SELECT name, is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    # Получаем список сеансов
    cur.execute('''
        SELECT id, movie_title, session_date, session_time 
        FROM sessions 
        ORDER BY session_date, session_time
    ''')
    sessions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('rgz/index.html',
                         user_name=user[0],
                         is_admin=user[1],
                         sessions=sessions,
                         student_name="Нейверт Арина Сергеевна",
                         group="ФБИ-33")

# Регистрация
@rgz.route('/rgz/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        login = request.form['login']
        password = request.form['password']
        
        if not name or not login or not password:
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('rgz/register.html',
                                 student_name="Нейверт Арина Сергеевна",
                                 group="ФБИ-33")
        
        if not validate_credentials(login, password):
            flash('Логин и пароль должны содержать только латинские буквы, цифры и знаки препинания', 'error')
            return render_template('rgz/register.html',
                                 student_name="Нейверт Арина Сергеевна",
                                 group="ФБИ-33")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cur.execute('SELECT id FROM users WHERE login = %s', (login,))
        if cur.fetchone():
            flash('Пользователь с таким логином уже существует', 'error')
            cur.close()
            conn.close()
            return render_template('rgz/register.html',
                                 student_name="Нейверт Арина Сергеевна",
                                 group="ФБИ-33")
        
        # Создаем пользователя
        password_hash = generate_password_hash(password)
        cur.execute('INSERT INTO users (name, login, password_hash) VALUES (%s, %s, %s) RETURNING id',
                   (name, login, password_hash))
        user_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        session['user_id'] = user_id
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('rgz.main'))
    
    return render_template('rgz/register.html',
                         student_name="Нейверт Арина Сергеевна",
                         group="ФБИ-33")

# Авторизация
@rgz.route('/rgz/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT id, password_hash FROM users WHERE login = %s', (login,))
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        flash('Вход выполнен успешно!', 'success')
    else:
        flash('Неверный логин или пароль', 'error')
    
    return redirect(url_for('rgz.main'))

# Выход
@rgz.route('/rgz/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('rgz.main'))

# Удаление аккаунта
@rgz.route('/rgz/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('rgz.main'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Удаляем бронирования пользователя
    cur.execute('DELETE FROM bookings WHERE user_id = %s', (session['user_id'],))
    # Удаляем пользователя
    cur.execute('DELETE FROM users WHERE id = %s', (session['user_id'],))
    
    conn.commit()
    cur.close()
    conn.close()
    
    session.pop('user_id', None)
    flash('Ваш аккаунт был удален', 'info')
    return redirect(url_for('rgz.main'))

# Просмотр сеанса - ОБНОВЛЕННАЯ ЛОГИКА
@rgz.route('/rgz/session/<int:session_id>')
def view_session(session_id):
    if 'user_id' not in session:
        return redirect(url_for('rgz.main'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем информацию о сеансе
    cur.execute('SELECT movie_title, session_date, session_time FROM sessions WHERE id = %s', (session_id,))
    session_info = cur.fetchone()
    
    if not session_info:
        flash('Сеанс не найден', 'error')
        return redirect(url_for('rgz.main'))
    
    # Проверяем, не прошел ли сеанс
    session_datetime = datetime.datetime.combine(session_info[1], session_info[2])
    is_past = session_datetime < datetime.datetime.now()
    
    # Получаем ВСЕ бронирования для этого сеанса с именами пользователей
    cur.execute('''
        SELECT b.seat_number, u.name, u.id as user_id
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        WHERE b.session_id = %s
    ''', (session_id,))
    
    bookings_data = cur.fetchall()
    
    # Создаем словарь для отображения занятых мест
    # Формат: {номер_места: {'name': имя_пользователя, 'user_id': id_пользователя}}
    bookings = {}
    for seat_number, user_name, user_id in bookings_data:
        bookings[seat_number] = {
            'name': user_name,
            'user_id': user_id
        }
    
    # Получаем бронирования текущего пользователя (только номера мест)
    cur.execute('''
        SELECT seat_number FROM bookings 
        WHERE session_id = %s AND user_id = %s
    ''', (session_id, session['user_id']))
    user_bookings = [row[0] for row in cur.fetchall()]
    
    # Получаем информацию о пользователе (является ли админом)
    cur.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    is_admin = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template('rgz/session.html',
                         session_id=session_id,
                         movie_title=session_info[0],
                         session_date=session_info[1],
                         session_time=session_info[2],
                         is_past=is_past,
                         bookings=bookings,  # Теперь передаем словарь с полной информацией
                         user_bookings=user_bookings,  # Список мест текущего пользователя
                         current_user_id=session['user_id'],  # ID текущего пользователя
                         is_admin=is_admin,
                         total_seats=30,
                         student_name="Нейверт Арина Сергеевна",
                         group="ФБИ-33")

# API: Бронирование места
@rgz.route('/rgz/api/book', methods=['POST'])
def api_book():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'})
    
    data = request.get_json()
    session_id = data.get('session_id')
    seat_number = data.get('seat_number')
    
    if not session_id or not seat_number:
        return jsonify({'success': False, 'message': 'Неверные данные'})
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Проверяем существование сеанса и не прошел ли он
    cur.execute('SELECT session_date, session_time FROM sessions WHERE id = %s', (session_id,))
    session_info = cur.fetchone()
    if not session_info:
        return jsonify({'success': False, 'message': 'Сеанс не найден'})
    
    session_datetime = datetime.datetime.combine(session_info[0], session_info[1])
    if session_datetime < datetime.datetime.now():
        return jsonify({'success': False, 'message': 'Нельзя бронировать места на прошедший сеанс'})
    
    # Проверяем, не занято ли место
    cur.execute('SELECT id FROM bookings WHERE session_id = %s AND seat_number = %s', (session_id, seat_number))
    if cur.fetchone():
        return jsonify({'success': False, 'message': 'Место уже занято'})
    
    # Проверяем, не превысил ли пользователь лимит в 5 мест
    cur.execute('SELECT COUNT(*) FROM bookings WHERE session_id = %s AND user_id = %s', (session_id, session['user_id']))
    if cur.fetchone()[0] >= 5:
        return jsonify({'success': False, 'message': 'Нельзя забронировать более 5 мест на один сеанс'})
    
    # Бронируем место
    try:
        cur.execute('INSERT INTO bookings (user_id, session_id, seat_number) VALUES (%s, %s, %s)',
                   (session['user_id'], session_id, seat_number))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Место забронировано'})
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Ошибка при бронировании'})

# API: Отмена бронирования
@rgz.route('/rgz/api/cancel_booking', methods=['POST'])
def api_cancel_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'})
    
    data = request.get_json()
    session_id = data.get('session_id')
    seat_number = data.get('seat_number')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Удаляем бронирование
    cur.execute('DELETE FROM bookings WHERE session_id = %s AND seat_number = %s AND user_id = %s',
               (session_id, seat_number, session['user_id']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    if cur.rowcount > 0:
        return jsonify({'success': True, 'message': 'Бронирование отменено'})
    else:
        return jsonify({'success': False, 'message': 'Бронирование не найдено'})

# Админка: Создание сеанса
@rgz.route('/rgz/admin/create_session', methods=['GET', 'POST'])
def admin_create_session():
    if 'user_id' not in session:
        return redirect(url_for('rgz.main'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user[0]:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.main'))
    
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        session_date = request.form['session_date']
        session_time = request.form['session_time']
        
        if not movie_title or not session_date or not session_time:
            flash('Все поля обязательны для заполнения', 'error')
            return render_template('rgz/admin_create_session.html',
                                 student_name="Нейверт Арина Сергеевна",
                                 group="ФБИ-33")
        
        # Создаем сеанс
        cur.execute('INSERT INTO sessions (movie_title, session_date, session_time) VALUES (%s, %s, %s)',
                   (movie_title, session_date, session_time))
        conn.commit()
        
        flash('Сеанс создан успешно', 'success')
        return redirect(url_for('rgz.main'))
    
    cur.close()
    conn.close()
    
    return render_template('rgz/admin_create_session.html',
                         student_name="Нейверт Арина Сергеевна",
                         group="ФБИ-33")

# Админка: Удаление сеанса
@rgz.route('/rgz/admin/delete_session/<int:session_id>')
def admin_delete_session(session_id):
    if 'user_id' not in session:
        return redirect(url_for('rgz.main'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user[0]:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.main'))
    
    # Удаляем бронирования и сеанс
    cur.execute('DELETE FROM bookings WHERE session_id = %s', (session_id,))
    cur.execute('DELETE FROM sessions WHERE id = %s', (session_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    flash('Сеанс удален', 'success')
    return redirect(url_for('rgz.main'))

# Админка: Снятие брони
@rgz.route('/rgz/admin/remove_booking', methods=['POST'])
def admin_remove_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'})
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not user[0]:
        return jsonify({'success': False, 'message': 'Доступ запрещен'})
    
    data = request.get_json()
    session_id = data.get('session_id')
    seat_number = data.get('seat_number')
    
    # Удаляем бронирование
    cur.execute('DELETE FROM bookings WHERE session_id = %s AND seat_number = %s',
               (session_id, seat_number))
    conn.commit()
    
    cur.close()
    conn.close()
    
    if cur.rowcount > 0:
        return jsonify({'success': True, 'message': 'Бронирование снято'})
    else:
        return jsonify({'success': False, 'message': 'Бронирование не найдено'})

# Инициализация БД при первом запуске
@rgz.before_app_request
def initialize():
    init_db()