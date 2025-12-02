from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import string
from datetime import datetime, date, timedelta
import re

# Создаем Blueprint для РГЗ
rgz_bp = Blueprint('rgz', __name__, url_prefix='/rgz')

# ФИО студента и группа (отображаются на каждой странице)
STUDENT_INFO = {
    'fio': 'Нейверт Арина Сергеевна',
    'group': 'ФБИ-33'
}

# Конфигурация кинотеатра
CINEMA_CONFIG = {
    'total_seats': 30,
    'max_seats_per_user': 5,
    'rows': 5,
    'cols': 6
}

def get_db_path():
    """Определяем правильный путь к БД"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'rgz_database.db')

def init_db():
    """Инициализация базы данных"""
    db_path = get_db_path()
    db_exists = os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица фильмов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration_minutes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица сеансов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            session_date DATE NOT NULL,
            session_time TIME NOT NULL,
            price DECIMAL(10,2) NOT NULL CHECK(price > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
        )
    ''')

    # Таблица бронирований
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            seat_number INTEGER NOT NULL CHECK(seat_number >= 1 AND seat_number <= 30),
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(session_id, seat_number)
        )
    ''')

    # Создаем администратора, если его еще нет
    cursor.execute('SELECT * FROM users WHERE login = ?', ('admin',))
    admin_exists = cursor.fetchone()

    if not admin_exists:
        password_hash = generate_password_hash('Admin123!')
        try:
            cursor.execute('''
                INSERT INTO users (login, password_hash, name, is_admin)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'Администратор Кинотеатра', True))
            print("Создан администратор по умолчанию: admin / Admin123!")
        except sqlite3.IntegrityError:
            print("Администратор уже существует")

    # Создаем тестовые фильмы, если их нет
    cursor.execute('SELECT COUNT(*) FROM movies')
    if cursor.fetchone()[0] == 0:
        test_movies = [
            ('Интерстеллар', 'Эпическая научно-фантастическая драма Кристофера Нолана о путешествии через червоточину', 169),
            ('Крестный отец', 'Классическая гангстерская сага о семье Корлеоне', 175),
            ('Побег из Шоушенка', 'История о надежде и дружбе в тюрьме', 142),
            ('Форрест Гамп', 'Жизнь человека с низким IQ, который стал свидетелем ключевых событий истории США', 142),
            ('Начало', 'Фильм о ворах, которые внедряются в сны', 148),
            ('Темный рыцарь', 'Бэтмен противостоит Джокеру', 152),
            ('Пираты Карибского моря', 'Приключения Джека Воробья', 143),
            ('Матрица', 'Хакер узнает правду о реальности', 136),
            ('Король Лев', 'История о львенке Симбе', 88),
            ('Титаник', 'История любви на затонувшем корабле', 195)
        ]
        
        for title, desc, duration in test_movies:
            cursor.execute('''
                INSERT INTO movies (title, description, duration_minutes)
                VALUES (?, ?, ?)
            ''', (title, desc, duration))

    # Создаем тестовые сеансы
    cursor.execute('SELECT COUNT(*) FROM sessions')
    if cursor.fetchone()[0] == 0:
        # Сеансы на сегодня и завтра
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Получаем ID фильмов
        cursor.execute('SELECT id FROM movies')
        movie_ids = [row[0] for row in cursor.fetchall()]
        
        times = ['10:00', '13:30', '17:00', '20:30', '23:00']
        prices = [300.00, 350.00, 400.00, 450.00, 500.00]
        
        for movie_id in movie_ids[:5]:  # Первые 5 фильмов
            for i, time in enumerate(times):
                # Сеанс на сегодня
                cursor.execute('''
                    INSERT INTO sessions (movie_id, session_date, session_time, price)
                    VALUES (?, ?, ?, ?)
                ''', (movie_id, today.strftime('%Y-%m-%d'), time, prices[i]))
                
                # Сеанс на завтра
                cursor.execute('''
                    INSERT INTO sessions (movie_id, session_date, session_time, price)
                    VALUES (?, ?, ?, ?)
                ''', (movie_id, tomorrow.strftime('%Y-%m-%d'), time, prices[i]))

    # Создаем тестовых пользователей (10 штук)
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = FALSE')
    user_count = cursor.fetchone()[0]
    
    if user_count < 10:
        test_users = [
            ('ivanov', 'Ivan123!', 'Иван Иванов'),
            ('petrov', 'Petr123!', 'Петр Петров'),
            ('sidorov', 'Sidor123!', 'Сидор Сидоров'),
            ('smirnov', 'Smirn123!', 'Алексей Смирнов'),
            ('kuznetsov', 'Kuzne123!', 'Дмитрий Кузнецов'),
            ('popova', 'Popov123!', 'Мария Попова'),
            ('sokolova', 'Sokol123!', 'Анна Соколова'),
            ('lebedeva', 'Lebed123!', 'Елена Лебедева'),
            ('kozlov', 'Kozlo123!', 'Сергей Козлов'),
            ('novikov', 'Novik123!', 'Павел Новиков')
        ]
        
        for login, password, name in test_users[:10-user_count]:
            password_hash = generate_password_hash(password)
            try:
                cursor.execute('''
                    INSERT INTO users (login, password_hash, name)
                    VALUES (?, ?, ?)
                ''', (login, password_hash, name))
            except sqlite3.IntegrityError:
                continue

    conn.commit()
    conn.close()

    if not db_exists:
        print("База данных RGZ успешно создана!")
    else:
        print("База данных RGZ подключена успешно")

def get_db_connection():
    """Подключение к базе данных"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Валидация логина и пароля
def is_valid_username_password(text):
    """Проверка на допустимые символы"""
    pattern = r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?~]+$'
    return bool(re.match(pattern, text)) and len(text) >= 3

def is_valid_name(name):
    """Проверка имени (только буквы и пробелы)"""
    pattern = r'^[A-Za-zА-Яа-яЁё\s]+$'
    return bool(re.match(pattern, name)) and len(name) >= 2

def is_valid_price(price):
    """Проверка цены"""
    try:
        price_float = float(price)
        return price_float > 0
    except ValueError:
        return False

def is_session_in_past(session_date_str, session_time_str):
    """Проверка, прошел ли сеанс"""
    try:
        session_datetime = datetime.strptime(f'{session_date_str} {session_time_str}', '%Y-%m-%d %H:%M:%S')
        return session_datetime < datetime.now()
    except ValueError:
        # Если время в формате без секунд
        try:
            session_datetime = datetime.strptime(f'{session_date_str} {session_time_str}', '%Y-%m-%d %H:%M')
            return session_datetime < datetime.now()
        except ValueError:
            return False

@rgz_bp.before_request
def before_request():
    g.student_info = STUDENT_INFO

# Главная страница
@rgz_bp.route('/')
def index():
    return render_template('rgz/index.html', 
                         student_info=STUDENT_INFO,
                         cinema_config=CINEMA_CONFIG,
                         is_authenticated='user_id' in session)

# Страница с сеансами
@rgz_bp.route('/sessions')
def sessions():
    conn = get_db_connection()
    
    # Получаем все сеансы с информацией о фильмах
    sessions_data = conn.execute('''
        SELECT s.*, m.title as movie_title, m.description as movie_description,
               m.duration_minutes,
               (SELECT COUNT(*) FROM bookings WHERE session_id = s.id) as booked_seats
        FROM sessions s
        JOIN movies m ON s.movie_id = m.id
        ORDER BY s.session_date, s.session_time
    ''').fetchall()
    
    conn.close()
    
    # Определяем, какие сеансы в прошлом
    sessions_list = []
    for session_item in sessions_data:
        is_past = is_session_in_past(session_item['session_date'], session_item['session_time'])
        sessions_list.append({
            **dict(session_item),
            'is_past': is_past,
            'available_seats': CINEMA_CONFIG['total_seats'] - session_item['booked_seats']
        })
    
    return render_template('rgz/sessions.html',
                         sessions=sessions_list,
                         student_info=STUDENT_INFO,
                         cinema_config=CINEMA_CONFIG,
                         is_authenticated='user_id' in session)

# Страница сеанса с местами
@rgz_bp.route('/session/<int:session_id>')
def session_detail(session_id):
    if 'user_id' not in session:
        flash('Для бронирования необходимо войти в систему', 'error')
        return redirect(url_for('rgz.login'))
    
    conn = get_db_connection()
    
    # Получаем информацию о сеансе
    session_data = conn.execute('''
        SELECT s.*, m.title as movie_title, m.description as movie_description
        FROM sessions s
        JOIN movies m ON s.movie_id = m.id
        WHERE s.id = ?
    ''', (session_id,)).fetchone()
    
    if not session_data:
        flash('Сеанс не найден', 'error')
        return redirect(url_for('rgz.sessions'))
    
    # Проверяем, не прошел ли сеанс
    is_past = is_session_in_past(session_data['session_date'], session_data['session_time'])
    
    # Получаем бронирования для этого сеанса
    bookings = conn.execute('''
        SELECT b.seat_number, u.name as user_name, u.id as user_id
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        WHERE b.session_id = ?
    ''', (session_id,)).fetchall()
    
    # Проверяем, сколько мест уже забронировал пользователь
    user_bookings_count = conn.execute('''
        SELECT COUNT(*) FROM bookings
        WHERE session_id = ? AND user_id = ?
    ''', (session_id, session['user_id'])).fetchone()[0]
    
    conn.close()
    
    can_book_more = user_bookings_count < CINEMA_CONFIG['max_seats_per_user']
    
    # Создаем карту мест
    seats = []
    booked_seats_by_user = {}
    
    for booking in bookings:
        booked_seats_by_user[booking['seat_number']] = {
            'user_name': booking['user_name'],
            'user_id': booking['user_id']
        }
    
    for seat_num in range(1, CINEMA_CONFIG['total_seats'] + 1):
        status = booked_seats_by_user.get(seat_num)
        seats.append({
            'number': seat_num,
            'row': ((seat_num - 1) // CINEMA_CONFIG['cols']) + 1,
            'col': ((seat_num - 1) % CINEMA_CONFIG['cols']) + 1,
            'booked': status is not None,
            'booked_by_current': status['user_id'] == session['user_id'] if status else False,
            'user_name': status['user_name'] if status else None
        })
    
    return render_template('rgz/session_detail.html',
                         session=session_data,
                         seats=seats,
                         cinema_config=CINEMA_CONFIG,
                         student_info=STUDENT_INFO,
                         is_past=is_past,
                         user_bookings_count=user_bookings_count,
                         can_book_more=can_book_more)

# API: Бронирование места
@rgz_bp.route('/api/book_seat/<int:session_id>/<int:seat_number>', methods=['POST'])
def book_seat(session_id, seat_number):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Необходима авторизация'}), 401
    
    # Проверяем валидность номера места
    if not (1 <= seat_number <= CINEMA_CONFIG['total_seats']):
        return jsonify({'success': False, 'error': 'Неверный номер места'}), 400
    
    conn = get_db_connection()
    
    # Проверяем, не прошел ли сеанс
    session_data = conn.execute('''
        SELECT * FROM sessions WHERE id = ?
    ''', (session_id,)).fetchone()
    
    if not session_data:
        conn.close()
        return jsonify({'success': False, 'error': 'Сеанс не найден'}), 404
    
    if is_session_in_past(session_data['session_date'], session_data['session_time']):
        conn.close()
        return jsonify({'success': False, 'error': 'Нельзя бронировать места на прошедший сеанс'}), 400
    
    # Проверяем, не занято ли место
    existing_booking = conn.execute('''
        SELECT * FROM bookings
        WHERE session_id = ? AND seat_number = ?
    ''', (session_id, seat_number)).fetchone()
    
    if existing_booking:
        conn.close()
        return jsonify({'success': False, 'error': 'Место уже занято'}), 400
    
    # Проверяем, не превысил ли пользователь лимит
    user_bookings_count = conn.execute('''
        SELECT COUNT(*) FROM bookings
        WHERE session_id = ? AND user_id = ?
    ''', (session_id, session['user_id'])).fetchone()[0]
    
    if user_bookings_count >= CINEMA_CONFIG['max_seats_per_user']:
        conn.close()
        return jsonify({'success': False, 'error': f'Нельзя бронировать более {CINEMA_CONFIG["max_seats_per_user"]} мест'}), 400
    
    # Бронируем место
    try:
        conn.execute('''
            INSERT INTO bookings (session_id, user_id, seat_number)
            VALUES (?, ?, ?)
        ''', (session_id, session['user_id'], seat_number))
        conn.commit()
        
        # Получаем имя пользователя для отображения
        user = conn.execute('SELECT name FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'user_name': user['name']
        })
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Ошибка при бронировании'}), 500

# API: Отмена бронирования
@rgz_bp.route('/api/cancel_booking/<int:session_id>/<int:seat_number>', methods=['POST'])
def cancel_booking(session_id, seat_number):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Необходима авторизация'}), 401
    
    conn = get_db_connection()
    
    # Проверяем, не прошел ли сеанс
    session_data = conn.execute('''
        SELECT * FROM sessions WHERE id = ?
    ''', (session_id,)).fetchone()
    
    if session_data and is_session_in_past(session_data['session_date'], session_data['session_time']):
        conn.close()
        return jsonify({'success': False, 'error': 'Нельзя отменять бронь на прошедший сеанс'}), 400
    
    # Удаляем бронирование (только свое)
    result = conn.execute('''
        DELETE FROM bookings
        WHERE session_id = ? AND seat_number = ? AND user_id = ?
    ''', (session_id, seat_number, session['user_id']))
    
    if result.rowcount > 0:
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    else:
        conn.close()
        return jsonify({'success': False, 'error': 'Бронь не найдена или у вас нет прав для ее отмены'}), 404

# Регистрация
@rgz_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name'].strip()
        
        # Валидация
        errors = []
        
        if not login or not password or not name:
            errors.append('Все поля обязательны для заполнения')
        
        if not is_valid_username_password(login):
            errors.append('Логин должен содержать только латинские буквы, цифры и специальные символы')
        
        if not is_valid_username_password(password):
            errors.append('Пароль должен содержать только латинские буквы, цифры и специальные символы')
        
        if len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        
        if password != confirm_password:
            errors.append('Пароли не совпадают')
        
        if not is_valid_name(name):
            errors.append('Имя должно содержать только буквы и пробелы')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('rgz/register.html', student_info=STUDENT_INFO)
        
        # Проверяем, не существует ли уже пользователь с таким логином
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT * FROM users WHERE login = ?', (login,)
        ).fetchone()
        
        if existing_user:
            flash('Пользователь с таким логином уже существует', 'error')
            conn.close()
            return render_template('rgz/register.html', student_info=STUDENT_INFO)
        
        # Хешируем пароль и сохраняем пользователя
        password_hash = generate_password_hash(password)
        
        try:
            conn.execute('''
                INSERT INTO users (login, password_hash, name)
                VALUES (?, ?, ?)
            ''', (login, password_hash, name))
            conn.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('rgz.login'))
            
        except sqlite3.IntegrityError:
            flash('Ошибка при регистрации', 'error')
        finally:
            conn.close()
    
    return render_template('rgz/register.html', student_info=STUDENT_INFO)

# Вход в систему
@rgz_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE login = ?', (login,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            session['user_name'] = user['name']
            session['is_admin'] = bool(user['is_admin'])
            flash(f'Добро пожаловать, {user["name"]}!', 'success')
            return redirect(url_for('rgz.sessions'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('rgz/login.html', student_info=STUDENT_INFO)

# Выход из системы
@rgz_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('rgz.index'))

# Удаление аккаунта
@rgz_bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash('Необходимо войти в систему', 'error')
        return redirect(url_for('rgz.login'))
    
    # Администратор не может удалить свой аккаунт через интерфейс
    if session.get('is_admin'):
        flash('Администратор не может удалить свой аккаунт через интерфейс', 'error')
        return redirect(url_for('rgz.profile'))
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    
    # Удаляем все бронирования пользователя
    conn.execute('DELETE FROM bookings WHERE user_id = ?', (user_id,))
    
    # Удаляем пользователя
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    session.clear()
    flash('Ваш аккаунт успешно удален', 'info')
    return redirect(url_for('rgz.index'))

# Профиль пользователя
@rgz_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Необходимо войти в систему', 'error')
        return redirect(url_for('rgz.login'))
    
    conn = get_db_connection()
    
    # Получаем информацию о пользователе
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    # Получаем бронирования пользователя
    bookings = conn.execute('''
        SELECT b.*, s.session_date, s.session_time, s.price,
               m.title as movie_title
        FROM bookings b
        JOIN sessions s ON b.session_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE b.user_id = ?
        ORDER BY s.session_date DESC, s.session_time DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    # Определяем, какие бронирования активные, а какие прошедшие
    bookings_with_status = []
    for booking in bookings:
        is_past = is_session_in_past(booking['session_date'], booking['session_time'])
        bookings_with_status.append({
            **dict(booking),
            'is_past': is_past
        })
    
    return render_template('rgz/profile.html',
                         user=user,
                         bookings=bookings_with_status,
                         student_info=STUDENT_INFO)

# Админ-панель
@rgz_bp.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    # Получаем статистику
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_movies = conn.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
    total_sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    
    # Получаем последние бронирования
    recent_bookings = conn.execute('''
        SELECT b.*, u.name as user_name, m.title as movie_title,
               s.session_date, s.session_time
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN sessions s ON b.session_id = s.id
        JOIN movies m ON s.movie_id = m.id
        ORDER BY b.booked_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('rgz/admin/index.html',
                         student_info=STUDENT_INFO,
                         total_users=total_users,
                         total_movies=total_movies,
                         total_sessions=total_sessions,
                         total_bookings=total_bookings,
                         recent_bookings=recent_bookings)

# Управление фильмами (админ)
@rgz_bp.route('/admin/movies', methods=['GET', 'POST'])
def admin_movies():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        duration = request.form['duration'].strip()
        
        errors = []
        
        if not title:
            errors.append('Название фильма обязательно')
        
        if not duration or not duration.isdigit():
            errors.append('Длительность должна быть числом')
        elif int(duration) <= 0:
            errors.append('Длительность должна быть положительным числом')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                conn.execute('''
                    INSERT INTO movies (title, description, duration_minutes)
                    VALUES (?, ?, ?)
                ''', (title, description, int(duration)))
                conn.commit()
                flash('Фильм успешно добавлен', 'success')
            except sqlite3.Error as e:
                flash(f'Ошибка при добавлении фильма: {str(e)}', 'error')
    
    # Получаем все фильмы
    movies = conn.execute('''
        SELECT m.*, 
               (SELECT COUNT(*) FROM sessions WHERE movie_id = m.id) as session_count
        FROM movies m
        ORDER BY m.title
    ''').fetchall()
    
    conn.close()
    
    return render_template('rgz/admin/movies.html',
                         movies=movies,
                         student_info=STUDENT_INFO)

# Удаление фильма (админ)
@rgz_bp.route('/admin/delete_movie/<int:movie_id>')
def admin_delete_movie(movie_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    # Проверяем, есть ли сеансы с этим фильмом
    sessions_count = conn.execute(
        'SELECT COUNT(*) FROM sessions WHERE movie_id = ?', (movie_id,)
    ).fetchone()[0]
    
    if sessions_count > 0:
        flash('Нельзя удалить фильм, для которого есть сеансы', 'error')
    else:
        conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        conn.commit()
        flash('Фильм успешно удален', 'success')
    
    conn.close()
    return redirect(url_for('rgz.admin_movies'))

# Управление сеансами (админ)
@rgz_bp.route('/admin/sessions', methods=['GET', 'POST'])
def admin_sessions():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    # Получаем все фильмы для выпадающего списка
    movies = conn.execute('SELECT id, title FROM movies ORDER BY title').fetchall()
    
    if request.method == 'POST':
        movie_id = request.form['movie_id']
        session_date = request.form['session_date']
        session_time = request.form['session_time']
        price = request.form['price']
        
        errors = []
        
        if not movie_id:
            errors.append('Необходимо выбрать фильм')
        
        if not session_date:
            errors.append('Дата сеанса обязательна')
        
        if not session_time:
            errors.append('Время сеанса обязательно')
        
        if not is_valid_price(price):
            errors.append('Цена должна быть положительным числом')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                conn.execute('''
                    INSERT INTO sessions (movie_id, session_date, session_time, price)
                    VALUES (?, ?, ?, ?)
                ''', (movie_id, session_date, session_time, float(price)))
                conn.commit()
                flash('Сеанс успешно добавлен', 'success')
            except sqlite3.Error as e:
                flash(f'Ошибка при добавлении сеанса: {str(e)}', 'error')
    
    # Получаем все сеансы с информацией о фильмах
    sessions_data = conn.execute('''
        SELECT s.*, m.title as movie_title,
               (SELECT COUNT(*) FROM bookings WHERE session_id = s.id) as booked_seats
        FROM sessions s
        JOIN movies m ON s.movie_id = m.id
        ORDER BY s.session_date DESC, s.session_time DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('rgz/admin/sessions.html',
                         sessions=sessions_data,
                         movies=movies,
                         student_info=STUDENT_INFO,
                         cinema_config=CINEMA_CONFIG)

# Удаление сеанса (админ)
@rgz_bp.route('/admin/delete_session/<int:session_id>')
def admin_delete_session(session_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    # Проверяем, есть ли бронирования
    bookings_count = conn.execute(
        'SELECT COUNT(*) FROM bookings WHERE session_id = ?', (session_id,)
    ).fetchone()[0]
    
    if bookings_count > 0:
        flash('Нельзя удалить сеанс, на который есть бронирования', 'error')
    else:
        conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        conn.commit()
        flash('Сеанс успешно удален', 'success')
    
    conn.close()
    return redirect(url_for('rgz.admin_sessions'))

# Снятие брони (админ)
@rgz_bp.route('/admin/cancel_booking/<int:booking_id>')
def admin_cancel_booking(booking_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()
    
    flash('Бронирование отменено администратором', 'success')
    return redirect(url_for('rgz.admin_panel'))

# Управление пользователями (админ)
@rgz_bp.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    conn = get_db_connection()
    
    users = conn.execute('''
        SELECT u.*,
               (SELECT COUNT(*) FROM bookings WHERE user_id = u.id) as booking_count
        FROM users u
        ORDER BY u.created_at DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('rgz/admin/users.html',
                         users=users,
                         student_info=STUDENT_INFO)

# Удаление пользователя (админ)
@rgz_bp.route('/admin/delete_user/<int:user_id>')
def admin_delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Доступ запрещен', 'error')
        return redirect(url_for('rgz.index'))
    
    # Нельзя удалить самого себя
    if user_id == session['user_id']:
        flash('Нельзя удалить свой собственный аккаунт', 'error')
        return redirect(url_for('rgz.admin_users'))
    
    conn = get_db_connection()
    
    # Удаляем все бронирования пользователя
    conn.execute('DELETE FROM bookings WHERE user_id = ?', (user_id,))
    
    # Удаляем пользователя
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    flash('Пользователь и все его бронирования удалены', 'success')
    return redirect(url_for('rgz.admin_users'))

# Автоматически инициализируем БД при импорте
print("Инициализация базы данных RGZ (Кинотеатр)...")
init_db()