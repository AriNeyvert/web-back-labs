from flask import Blueprint, render_template, jsonify, request, session
import json
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sqlite3
from datetime import datetime

lab9 = Blueprint('lab9', __name__,
                 template_folder='templates/lab9',
                 static_folder='static/lab9')

# Новогодние поздравления
congratulations = [
    "С Новым годом! Желаю счастья и здоровья!",
    "Пусть новый год принесет много радости!",
    "Желаю исполнения всех желаний в новом году!",
    "Пусть каждый день нового года будет наполнен волшебством!",
    "Счастья, любви и процветания в новом году!",
    "Пусть ангел-хранитель оберегает вас весь год!",
    "Желаю финансового благополучия и стабильности!",
    "Пусть все мечты сбудутся в новом году!",
    "Здоровья вам и вашим близким в новом году!",
    "Желаю интересных путешествий и новых открытий!"
]

# Функции для работы с базой данных
def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('lab9_gifts.db')
    cursor = conn.cursor()
    
    # Таблица для позиций коробок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gift_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gift_id INTEGER UNIQUE NOT NULL,
            top REAL NOT NULL,
            left_pos REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица для открытых коробок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opened_boxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gift_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            ip_address TEXT,
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (gift_id) REFERENCES gift_positions (gift_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect('lab9_gifts.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def save_gift_position(gift_id, position):
    """Сохранение позиции коробки в БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO gift_positions (gift_id, top, left_pos)
            VALUES (?, ?, ?)
        ''', (gift_id, position['top'], position['left']))
        conn.commit()
    except Exception as e:
        print(f"Error saving gift position: {e}")
    finally:
        conn.close()

def get_gift_position(gift_id):
    """Получение позиции коробки из БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT top, left_pos FROM gift_positions WHERE gift_id = ?', (gift_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {'top': result['top'], 'left': result['left_pos']}
    return None

def get_all_gift_positions():
    """Получение всех позиций коробок"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT gift_id, top, left_pos FROM gift_positions ORDER BY gift_id')
    results = cursor.fetchall()
    conn.close()
    
    positions = {}
    for row in results:
        positions[str(row['gift_id'])] = {'top': row['top'], 'left': row['left_pos']}
    return positions

def is_gift_opened(gift_id):
    """Проверка, открыта ли коробка (любым пользователем)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM opened_boxes WHERE gift_id = ?', (gift_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['count'] > 0

def mark_gift_as_opened(gift_id, session_id, ip_address):
    """Отметить коробку как открытую"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO opened_boxes (gift_id, session_id, ip_address)
        VALUES (?, ?, ?)
    ''', (gift_id, session_id, ip_address))
    
    conn.commit()
    conn.close()

def count_opened_by_user(session_id):
    """Подсчет коробок, открытых текущим пользователем"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM opened_boxes WHERE session_id = ?', (session_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['count']

def count_total_opened():
    """Общее количество открытых коробок"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(DISTINCT gift_id) as count FROM opened_boxes')
    result = cursor.fetchone()
    conn.close()
    
    return result['count']

def get_opened_gifts():
    """Получение списка открытых коробок"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT gift_id FROM opened_boxes ORDER BY gift_id')
    results = cursor.fetchall()
    conn.close()
    
    return [row['gift_id'] for row in results]

def generate_random_position(gift_id, occupied_positions, max_attempts=100):
    """Генерирует случайную позицию, избегая защищенных зон и других коробок"""
    
    # Определяем защищенные зоны (в процентах от размера контейнера)
    # 1. Зона инструкций (верхняя часть - первые 15% высоты)
    # 2. Зона кнопки сброса (нижняя часть - 85-100% высоты, 35-65% ширины)
    protected_areas = [
        {'top': 0, 'left': 0, 'width': 100, 'height': 15},  # Инструкции
        {'top': 85, 'left': 35, 'width': 30, 'height': 15}   # Кнопка сброса
    ]
    
    for attempt in range(max_attempts):
        # Генерируем случайные координаты (в процентах)
        top = random.uniform(15, 70)  # 15-70% от верха
        left = random.uniform(5, 80)   # 5-80% от левого края
        
        # Размер коробки примерно 15% от размера контейнера
        box_size = 15
        
        # Проверяем, не попадает ли коробка в защищенную зону
        in_protected_area = False
        for area in protected_areas:
            if not (left + box_size < area['left'] or 
                    left > area['left'] + area['width'] or
                    top + box_size < area['top'] or 
                    top > area['top'] + area['height']):
                in_protected_area = True
                break
        
        if in_protected_area:
            continue
        
        # Проверяем расстояние до других коробок
        too_close = False
        for pos in occupied_positions:
            # Рассчитываем расстояние между центрами коробок
            center_x1 = left + box_size / 2
            center_y1 = top + box_size / 2
            center_x2 = pos['left'] + box_size / 2
            center_y2 = pos['top'] + box_size / 2
            
            distance = ((center_x1 - center_x2) ** 2 + (center_y1 - center_y2) ** 2) ** 0.5
            
            # Если расстояние меньше 20% - слишком близко
            if distance < 20:
                too_close = True
                break
        
        if too_close:
            continue
        
        # Если все проверки пройдены, возвращаем позицию
        return {'top': round(top, 2), 'left': round(left, 2)}
    
    # Если не удалось найти позицию, используем предопределенные позиции
    default_positions = [
        {'top': 15, 'left': 10}, {'top': 15, 'left': 30}, {'top': 15, 'left': 50}, {'top': 15, 'left': 70},
        {'top': 35, 'left': 10}, {'top': 35, 'left': 30}, {'top': 35, 'left': 50}, {'top': 35, 'left': 70},
        {'top': 55, 'left': 20}, {'top': 55, 'left': 60}
    ]
    
    if gift_id < len(default_positions):
        return default_positions[gift_id]
    else:
        return {'top': 20, 'left': 20}

def init_gifts():
    """Инициализация данных о подарках"""
    # Инициализируем базу данных
    init_db()
    
    # Проверяем наличие папки для статики
    static_path = Path(__file__).parent / "static" / "lab9"
    static_path.mkdir(parents=True, exist_ok=True)
    
    # Создаем картинку для открытого подарка
    opened_file = static_path / "opened.jpg"
    if not opened_file.exists():
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        d = ImageDraw.Draw(img)
        
        d.rectangle([40, 40, 160, 160], outline=(200, 200, 200), width=3)
        d.line([100, 40, 100, 160], fill=(200, 200, 200), width=2)
        d.line([40, 100, 160, 100], fill=(200, 200, 200), width=2)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        d.text((60, 80), "Открыто", fill=(255, 255, 255), font=font)
        img.save(opened_file)

def get_gifts_data():
    """Получение данных о всех подарках"""
    # Получаем все позиции из БД
    positions = get_all_gift_positions()
    
    # Перемешиваем поздравления
    random_congrats = congratulations.copy()
    random.shuffle(random_congrats)
    
    # Получаем список открытых коробок
    opened_gifts = get_opened_gifts()
    
    # Создаем словарь с данными о подарках
    gifts = {}
    for i in range(10):
        gift_id = str(i)
        
        # Получаем или создаем позицию
        if gift_id in positions:
            position = positions[gift_id]
        else:
            # Получаем занятые позиции
            occupied = []
            for j in range(i):
                occupied_id = str(j)
                if occupied_id in positions:
                    occupied.append(positions[occupied_id])
            
            # Генерируем новую позицию
            position = generate_random_position(i, occupied)
            save_gift_position(i, position)
        
        # Проверяем, открыта ли коробка
        opened = int(gift_id) in opened_gifts
        
        gifts[gift_id] = {
            'id': i,
            'congratulation': random_congrats[i],
            'gift_image': f'gift{i+1}.jpg',
            'opened': opened,
            'position': position
        }
    
    return gifts

@lab9.route('/lab9/')
def lab9_index():
    """Главная страница lab9"""
    init_gifts()
    return render_template('lab9/lab9.html')

@lab9.route('/lab9/get_gifts')
def get_gifts():
    """Получение данных о подарках"""
    gifts_data = get_gifts_data()
    
    # Получаем ID открытых коробок текущим пользователем
    user_session_id = session.get('session_id')
    if not user_session_id:
        # Создаем новый ID сессии
        user_session_id = os.urandom(16).hex()
        session['session_id'] = user_session_id
    
    # Подсчитываем количество неоткрытых коробок
    unopened_count = sum(1 for gift in gifts_data.values() if not gift['opened'])
    
    # Получаем количество коробок, открытых текущим пользователем
    user_opened_count = count_opened_by_user(user_session_id)
    
    return jsonify({
        'gifts': gifts_data,
        'unopened_count': unopened_count,
        'opened_count': user_opened_count,
        'total_gifts': len(gifts_data)
    })

@lab9.route('/lab9/open_gift', methods=['POST'])
def open_gift():
    """Открытие подарка"""
    data = request.json
    gift_id = int(data.get('gift_id', -1))
    
    if gift_id < 0 or gift_id >= 10:
        return jsonify({'error': 'Неверный ID подарка'}), 400
    
    # Получаем ID сессии
    user_session_id = session.get('session_id')
    if not user_session_id:
        return jsonify({'error': 'Сессия не найдена'}), 400
    
    # Проверяем, сколько коробок уже открыл пользователь
    user_opened_count = count_opened_by_user(user_session_id)
    if user_opened_count >= 3:
        return jsonify({'error': 'Вы уже открыли максимальное количество коробок (3)!'}), 400
    
    # Проверяем, не открыта ли уже эта коробка
    if is_gift_opened(gift_id):
        return jsonify({'error': 'Эта коробка уже пуста!'}), 400
    
    # Проверяем, не открывал ли пользователь уже эту коробку
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM opened_boxes WHERE gift_id = ? AND session_id = ?', 
                   (gift_id, user_session_id))
    result = cursor.fetchone()
    conn.close()
    
    if result['count'] > 0:
        return jsonify({'error': 'Вы уже открыли эту коробку!'}), 400
    
    # Получаем IP-адрес пользователя
    ip_address = request.remote_addr
    
    # Отмечаем коробку как открытую
    mark_gift_as_opened(gift_id, user_session_id, ip_address)
    
    # Получаем обновленные данные
    gifts_data = get_gifts_data()
    
    # Подсчитываем количество неоткрытых коробок
    unopened_count = sum(1 for gift in gifts_data.values() if not gift['opened'])
    
    # Увеличиваем счетчик открытых пользователем коробок
    user_opened_count += 1
    
    return jsonify({
        'success': True,
        'congratulation': congratulations[gift_id],
        'gift_image': f'gift{gift_id + 1}.jpg',
        'opened_count': user_opened_count,
        'unopened_count': unopened_count,
        'total_gifts': len(gifts_data)
    })

@lab9.route('/lab9/reset', methods=['POST'])
def reset_gifts():
    """Сброс всех подарков (для тестирования)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Очищаем все таблицы
    cursor.execute('DELETE FROM opened_boxes')
    cursor.execute('DELETE FROM gift_positions')
    
    # Сбрасываем автоинкремент
    cursor.execute('DELETE FROM sqlite_sequence')
    
    conn.commit()
    conn.close()
    
    # Очищаем сессию пользователя
    session.pop('session_id', None)
    
    return jsonify({
        'success': True,
        'message': 'Все подарки сброшены!'
    })

@lab9.route('/lab9/check_opened')
def check_opened():
    """Проверка открытых коробок текущим пользователем"""
    user_session_id = session.get('session_id')
    if not user_session_id:
        return jsonify({'opened_boxes': [], 'count': 0})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT gift_id FROM opened_boxes WHERE session_id = ?', (user_session_id,))
    results = cursor.fetchall()
    conn.close()
    
    opened_boxes = [row['gift_id'] for row in results]
    
    return jsonify({
        'opened_boxes': opened_boxes,
        'count': len(opened_boxes)
    })

@lab9.route('/lab9/get_stats')
def get_stats():
    """Получение статистики по подаркам"""
    gifts_data = get_gifts_data()
    
    # Общее количество подарков
    total = len(gifts_data)
    
    # Количество открытых подарков (всем пользователям)
    opened_total = count_total_opened()
    
    # Количество открытых текущим пользователем
    user_session_id = session.get('session_id')
    opened_user = count_opened_by_user(user_session_id) if user_session_id else 0
    
    # Количество доступных для открытия
    available = total - opened_total
    
    # Сколько еще может открыть пользователь
    user_can_open = min(3 - opened_user, available)
    
    return jsonify({
        'total': total,
        'opened_total': opened_total,
        'opened_user': opened_user,
        'available': available,
        'user_can_open': user_can_open
    })

@lab9.route('/lab9/admin/reset_all', methods=['POST'])
def admin_reset_all():
    """Полный сброс (только для администратора)"""
    # Можно добавить проверку прав администратора
    return reset_gifts()
