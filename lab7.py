from flask import Blueprint, render_template, jsonify, abort, request, g
import sqlite3
from datetime import datetime
import os

lab7 = Blueprint('lab7', __name__)

# Конфигурация БД
DATABASE = 'films.db'

def get_db():
    """Получение соединения с БД"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@lab7.teardown_request
def close_connection(exception):
    """Закрытие соединения с БД"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Инициализация БД"""
    db = get_db()
    
    # Создаем таблицу
    db.execute('''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_ru TEXT NOT NULL,
            year INTEGER NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем индексы
    db.execute('CREATE INDEX IF NOT EXISTS idx_films_year ON films(year)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_films_title ON films(title)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_films_title_ru ON films(title_ru)')
    
    # Проверяем, есть ли данные
    cursor = db.execute('SELECT COUNT(*) FROM films')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Добавляем начальные данные
        initial_films = [
            (
                "Interstellar",
                "Интерстеллар",
                2014,
                "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планета с подходящими для человечества условиями."
            ),
            (
                "The Shawshank Redemption",
                "Побег из Шоушенка",
                1994,
                "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки. Каждый, кто попадает в эти стены, становится их рабом до конца жизни. Но Энди, обладающий живым умом и доброй душой, находит подход как к заключённым, так и к охранникам, добиваясь их особого к себе расположения."
            ),
            (
                "The Gentlemen",
                "Джентельмены",
                2019,
                "Один ушлый американец ещё со студенческих лет приторговывал наркотиками, а теперь придумал схему нелегального обогащения с использованием поместий обедневшей английской аристократии и очень неплохо на этом разбогател. Другой пронырливый журналист приходит к Рэю, правой руке американца, и предлагает тому купить киносценарий, в котором подробно описаны преступления его босса при участии других представителей лондонского криминального мира — партнёра-еврея, китайской диаспоры, чернокожих спортсменов и даже русского олигарха."
            ),
            (
                "The Green Mile",
                "Зеленая миля",
                1999,
                "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора», каждый из узников которого однажды проходит «зеленую милю» по пути к месту казни. Пол повидал много заключённых и надзирателей за время работы. Однако гигант Джон Коффи, обвинённый в страшном преступлении, стал одним из самых необычных обитателей блока."
            ),
            (
                "Shutter Island",
                "Остров проклятых",
                2010,
                "Два американских судебных пристава отправляются на один из островов в штате Массачусетс, чтобы расследовать исчезновение пациентки клиники для умалишенных преступников. При проведении расследования им придется столкнуться с паутиной лжи, обрушившимся ураганом и смертельным бунтом обитателей клиники."
            ),
        ]
        
        for film in initial_films:
            db.execute(
                'INSERT INTO films (title, title_ru, year, description) VALUES (?, ?, ?, ?)',
                film
            )
    
    db.commit()

# Инициализируем БД при первом запросе
@lab7.before_request
def before_request():
    init_db()

@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')

def validate_film_data(film):
    """Валидация данных фильма"""
    errors = {}
    
    # Получаем текущий год для проверки
    current_year = datetime.now().year
    
    # Проверка русского названия
    title_ru = film.get('title_ru', '').strip()
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно для заполнения'
    elif len(title_ru) > 200:
        errors['title_ru'] = 'Русское название не должно превышать 200 символов'
    
    # Проверка оригинального названия
    title = film.get('title', '').strip()
    
    if not title and not title_ru:
        errors['title'] = 'Название (оригинальное или русское) обязательно для заполнения'
    elif title and len(title) > 200:
        errors['title'] = 'Оригинальное название не должно превышать 200 символов'
    elif not title:
        # Если оригинальное название пустое, используем русское
        film['title'] = title_ru
    
    # Проверка года
    year = film.get('year')
    if not year:
        errors['year'] = 'Год обязателен для заполнения'
    else:
        try:
            year_int = int(year)
            if year_int < 1895 or year_int > current_year:
                errors['year'] = f'Год должен быть от 1895 до {current_year}'
        except (ValueError, TypeError):
            errors['year'] = 'Год должен быть числом'
    
    # Проверка описания
    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно для заполнения'
    elif len(description) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    
    return errors

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    """Получение всех фильмов"""
    db = get_db()
    cursor = db.execute('SELECT * FROM films ORDER BY year DESC, title_ru')
    films = cursor.fetchall()
    
    # Преобразуем Row объекты в список словарей
    films_list = []
    for film in films:
        films_list.append({
            'id': film['id'],
            'title': film['title'],
            'title_ru': film['title_ru'],
            'year': film['year'],
            'description': film['description'],
            'created_at': film['created_at']
        })
    
    return jsonify(films_list)

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    """Получение фильма по ID"""
    db = get_db()
    cursor = db.execute('SELECT * FROM films WHERE id = ?', (id,))
    film = cursor.fetchone()
    
    if film is None:
        abort(404, description=f"Фильм с id={id} не найден")
    
    return jsonify({
        'id': film['id'],
        'title': film['title'],
        'title_ru': film['title_ru'],
        'year': film['year'],
        'description': film['description'],
        'created_at': film['created_at']
    })

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    """Удаление фильма по ID"""
    db = get_db()
    
    # Проверяем существование фильма
    cursor = db.execute('SELECT id FROM films WHERE id = ?', (id,))
    film = cursor.fetchone()
    
    if film is None:
        abort(404, description=f"Фильм с id={id} не найден. Нельзя удалить несуществующий элемент.")
    
    # Удаляем фильм
    db.execute('DELETE FROM films WHERE id = ?', (id,))
    db.commit()
    
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    """Обновление фильма по ID"""
    db = get_db()
    
    # Проверяем существование фильма
    cursor = db.execute('SELECT id FROM films WHERE id = ?', (id,))
    film = cursor.fetchone()
    
    if film is None:
        abort(404, description=f"Фильм с id={id} не найден. Нельзя обновить несуществующий элемент.")
    
    # Получаем данные
    film_data = request.get_json()
    
    # Валидация данных
    errors = validate_film_data(film_data)
    if errors:
        return jsonify(errors), 400
    
    # Обновляем фильм
    db.execute(
        '''UPDATE films 
           SET title = ?, title_ru = ?, year = ?, description = ? 
           WHERE id = ?''',
        (film_data['title'], film_data['title_ru'], film_data['year'], 
         film_data['description'], id)
    )
    db.commit()
    
    # Возвращаем обновленный фильм
    cursor = db.execute('SELECT * FROM films WHERE id = ?', (id,))
    updated_film = cursor.fetchone()
    
    return jsonify({
        'id': updated_film['id'],
        'title': updated_film['title'],
        'title_ru': updated_film['title_ru'],
        'year': updated_film['year'],
        'description': updated_film['description'],
        'created_at': updated_film['created_at']
    })

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    """Добавление нового фильма"""
    db = get_db()
    
    # Получаем данные
    film_data = request.get_json()
    
    # Валидация данных
    errors = validate_film_data(film_data)
    if errors:
        return jsonify(errors), 400
    
    # Вставляем новый фильм
    cursor = db.execute(
        '''INSERT INTO films (title, title_ru, year, description) 
           VALUES (?, ?, ?, ?)''',
        (film_data['title'], film_data['title_ru'], film_data['year'], 
         film_data['description'])
    )
    
    db.commit()
    
    # Получаем ID нового фильма
    new_id = cursor.lastrowid
    
    return jsonify({"id": new_id}), 201

# Дополнительные эндпоинты для статистики
@lab7.route('/lab7/rest-api/stats/', methods=['GET'])
def get_stats():
    """Получение статистики по фильмам"""
    db = get_db()
    
    cursor = db.execute('SELECT COUNT(*) as count FROM films')
    total_films = cursor.fetchone()['count']
    
    cursor = db.execute('SELECT MIN(year) as min_year, MAX(year) as max_year FROM films')
    years = cursor.fetchone()
    
    cursor = db.execute('SELECT COUNT(*) as count FROM films WHERE year >= 2000')
    films_21st_century = cursor.fetchone()['count']
    
    cursor = db.execute('''
        SELECT year, COUNT(*) as film_count 
        FROM films 
        GROUP BY year 
        ORDER BY year DESC
        LIMIT 10
    ''')
    films_by_year = cursor.fetchall()
    
    return jsonify({
        'total_films': total_films,
        'min_year': years['min_year'],
        'max_year': years['max_year'],
        'films_21st_century': films_21st_century,
        'films_by_year': [
            {'year': row['year'], 'film_count': row['film_count']} 
            for row in films_by_year
        ]
    })

@lab7.route('/lab7/rest-api/search/', methods=['GET'])
def search_films():
    """Поиск фильмов по названию"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    db = get_db()
    cursor = db.execute(
        '''SELECT * FROM films 
           WHERE title_ru LIKE ? OR title LIKE ? 
           ORDER BY year DESC 
           LIMIT 20''',
        (f'%{query}%', f'%{query}%')
    )
    
    films = cursor.fetchall()
    
    films_list = []
    for film in films:
        films_list.append({
            'id': film['id'],
            'title': film['title'],
            'title_ru': film['title_ru'],
            'year': film['year'],
            'description': film['description'][:100] + '...' if len(film['description']) > 100 else film['description']
        })
    
    return jsonify(films_list)