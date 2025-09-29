from flask import Flask, url_for, request, redirect, abort, render_template
import datetime

app = Flask(__name__)

# Глобальная переменная для хранения лога 404 ошибок
error_log = []

# Список книг для отображения
books = [
    {'author': 'Фёдор Достоевский', 'title': 'Преступление и наказание', 'genre': 'Роман', 'pages': 671},
    {'author': 'Лев Толстой', 'title': 'Война и мир', 'genre': 'Роман-эпопея', 'pages': 1225},
    {'author': 'Михаил Булгаков', 'title': 'Мастер и Маргарита', 'genre': 'Роман', 'pages': 480},
    {'author': 'Антон Чехов', 'title': 'Рассказы', 'genre': 'Рассказ', 'pages': 350},
    {'author': 'Александр Пушкин', 'title': 'Евгений Онегин', 'genre': 'Роман в стихах', 'pages': 240},
    {'author': 'Николай Гоголь', 'title': 'Мёртвые души', 'genre': 'Поэма', 'pages': 352},
    {'author': 'Иван Тургенев', 'title': 'Отцы и дети', 'genre': 'Роман', 'pages': 288},
    {'author': 'Александр Дюма', 'title': 'Граф Монте-Кристо', 'genre': 'Приключенческий роман', 'pages': 928},
    {'author': 'Джордж Оруэлл', 'title': '1984', 'genre': 'Антиутопия', 'pages': 328},
    {'author': 'Рэй Брэдбери', 'title': '451° по Фаренгейту', 'genre': 'Научная фантастика', 'pages': 256},
    {'author': 'Джоан Роулинг', 'title': 'Гарри Поттер и философский камень', 'genre': 'Фэнтези', 'pages': 432},
    {'author': 'Джон Толкин', 'title': 'Властелин колец', 'genre': 'Фэнтези', 'pages': 1137}
]

# Список кошек для нового обработчика
cats = [
    {
        'name': 'Британская короткошёрстная',
        'image': 'british.jpg',
        'description': 'Популярная порода с плюшевой шерстью и круглыми глазами. Спокойные и интеллигентные.',
        'origin': 'Великобритания',
        'weight': '4-8 кг'
    },
    {
        'name': 'Мейн-кун',
        'image': 'maine_coon.jpg',
        'description': 'Крупная порода с длинной шерстью и кисточками на ушах. Дружелюбные и игривые.',
        'origin': 'США',
        'weight': '5-11 кг'
    },
    {
        'name': 'Сиамская',
        'image': 'siamese.jpg',
        'description': 'Элегантная кошка с голубыми глазами и характерным окрасом. Очень разговорчивые и общительные.',
        'origin': 'Таиланд',
        'weight': '3-5 кг'
    },
    {
        'name': 'Сфинкс',
        'image': 'sphynx.jpg',
        'description': 'Бесшёрстная порода с морщинистой кожей. Теплолюбивые и очень ласковые.',
        'origin': 'Канада',
        'weight': '3-5 кг'
    },
    {
        'name': 'Персидская',
        'image': 'persian.jpg',
        'description': 'Длинношёрстная порода с приплюснутой мордочкой. Спокойные и аристократичные.',
        'origin': 'Иран',
        'weight': '3-7 кг'
    },
    {
        'name': 'Бенгальская',
        'image': 'bengal.jpg',
        'description': 'Порода с леопардовым окрасом. Активные и любознательные, сохранили диковатый вид.',
        'origin': 'США',
        'weight': '4-7 кг'
    },
    {
        'name': 'Русская голубая',
        'image': 'russian_blue.jpg',
        'description': 'Кошка с серебристо-голубой шерстью и зелёными глазами. Скромные и преданные.',
        'origin': 'Россия',
        'weight': '3-5 кг'
    },
    {
        'name': 'Норвежская лесная',
        'image': 'norwegian_forest.jpg',
        'description': 'Крупная кошка с густой водонепроницаемой шерстью. Отличные охотники и лазальщики.',
        'origin': 'Норвегия',
        'weight': '4-9 кг'
    },
    {
        'name': 'Шотландская вислоухая',
        'image': 'scottish_fold.jpg',
        'description': 'Порода с загнутыми вперёд ушами. Дружелюбные и адаптируемые к разным условиям.',
        'origin': 'Шотландия',
        'weight': '3-6 кг'
    },
    {
        'name': 'Абиссинская',
        'image': 'abyssinian.jpg',
        'description': 'Стройная кошка с тикированной шерстью. Очень активные и любопытные.',
        'origin': 'Эфиопия',
        'weight': '3-5 кг'
    },
    {
        'name': 'Рэгдолл',
        'image': 'ragdoll.jpg',
        'description': 'Крупная кошка с голубыми глазами. Расслабляются на руках как тряпичные куклы.',
        'origin': 'США',
        'weight': '4-9 кг'
    },
    {
        'name': 'Ориентальная',
        'image': 'oriental.jpg',
        'description': 'Стройная кошка с большими ушами. Очень разговорчивые и привязчивые.',
        'origin': 'Таиланд',
        'weight': '3-5 кг'
    },
    {
        'name': 'Сибирская',
        'image': 'siberian.jpg',
        'description': 'Крупная кошка с густой трёхслойной шерстью. Сильные и ловкие, гипоаллергенная порода.',
        'origin': 'Россия',
        'weight': '4-9 кг'
    },
    {
        'name': 'Бирманская',
        'image': 'birman.jpg',
        'description': 'Полудлинношёрстная кошка с белыми "носочками". Спокойные и общительные.',
        'origin': 'Мьянма',
        'weight': '3-6 кг'
    },
    {
        'name': 'Турецкий ван',
        'image': 'turkish_van.jpg',
        'description': 'Кошка с любовью к воде и плаванию. Активные и интеллигентные.',
        'origin': 'Турция',
        'weight': '4-9 кг'
    },
    {
        'name': 'Египетский мау',
        'image': 'egyptian_mau.jpg',
        'description': 'Единственная естественная порода с пятнистым окрасом. Быстрые и грациозные.',
        'origin': 'Египет',
        'weight': '3-5 кг'
    },
    {
        'name': 'Манчкин',
        'image': 'munchkin.jpg',
        'description': 'Порода с короткими лапами. Несмотря на короткие ноги, очень подвижные и игривые.',
        'origin': 'США',
        'weight': '3-4 кг'
    },
    {
        'name': 'Девон-рекс',
        'image': 'devon_rex.jpg',
        'description': 'Кошка с волнистой шерстью и большими ушами. Очень активные и любвеобильные.',
        'origin': 'Великобритания',
        'weight': '3-4 кг'
    },
    {
        'name': 'Корниш-рекс',
        'image': 'cornish_rex.jpg',
        'description': 'Кошка с кудрявой шерстью и стройным телом. Энергичные и любознательные.',
        'origin': 'Великобритания',
        'weight': '3-5 кг'
    },
    {
        'name': 'Тойгер',
        'image': 'toyger.jpg',
        'description': 'Порода с тигровым окрасом. Дружелюбные и общительные, напоминают мини-тигров.',
        'origin': 'США',
        'weight': '4-7 кг'
    }
]

@app.route("/")
@app.route("/index")
def index():
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>НГТУ, ФБ, Лабораторные работы</title>
    </head>
    <body>
        <h1>НГТУ, ФБ, WEB-программирование, часть 2.<br> Список лабораторных</h1>
        <ul>
            <li><a href="/lab1">Первая лабораторная</a></li>
            <li><a href="/lab2">Вторая лабораторная</a></li>
        </ul>
        <footer>
            <p>Нейверт Арина Сергеевна</p>
            <p>Группа: ФБИ-33</p>
            <p>Курс: 3</p>
            <p>2025 год</p>
        </footer>
    </body>
</html>
'''

@app.route("/lab1/web")
def web():
    return """<!doctype html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
               <a href="/author">author</a>
           </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author")
def author():
    name = "Иванов Иван Иванович"
    group = "ФБИ-00"
    faculty = "ФБ"
    
    return """<!doctype html>
        <html>
            <body>
                <p>Студент: """+ name + """</p> 
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/lab1/web">web</a>
            </body>
        </html>"""

@app.route("/lab1/image")
def image():
    path = url_for("static", filename="oak.jpg")
    css = url_for ("static", filename="lab1.css")
    return f'''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Дуб</title>
        <link rel="stylesheet" href="{css}">
    </head> 
    <body>
        <h1>Дуб</h1>
        <img src="{path}" alt="oak">
    </body>
</html> ''', 200, {
    'Content-Language': "ru",
    'Number_lab' : "LABA_1",
    'Student' : "Neyvert Arina"
}

count = 0
@app.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + str(url) + '''<br>
        Ваш IP-адрес: ''' + str(client_ip) + '''<br>
        <br>
        <a href="/lab1/r_counter">Очистить счетчик</a>
    </body>
</html>
'''

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201

@app.route('/lab1/r_counter')
def r_counter():
    global count
    count = 0
    return redirect('/lab1/counter')

@app.route('/lab1')
def lab1():
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Лабораторная 1</title>
    </head>
    <body>
        <p>
        Flask — фреймворк для создания веб-приложений на языке программирования Python, 
        использующий набор инструментов Werkzeug, а также шаблонизатор Jinja2. 
        Относится к категории так называемых микрофреймворков — минималистичных каркасов веб-приложений, 
        сознательно предоставляющих лишь самые базовые возможности.
        </p>
        <hr>
        <a href="/">На главную</a>
        <h2>Список роутов</h2>
        <ul>
            <li><a href="/lab1/web">/lab1/web</a></li>
            <li><a href="/lab1/author">/lab1/author</a></li>
            <li><a href="/lab1/image">/lab1/image</a></li>
            <li><a href="/lab1/counter">/lab1/counter</a></li>
            <li><a href="/lab1/reset_counter">/lab1/reset_counter</a></li>
            <li><a href="/lab1/info">/lab1/info</a></li>
            <li><a href="/lab1/created">/lab1/created</a></li>
            <li><a href="/cause_error">/cause_error</a></li>
            <li><a href="/error/400">/error/400</a></li>
            <li><a href="/error/401">/error/401</a></li>
            <li><a href="/error/402">/error/402</a></li>
            <li><a href="/error/403">/error/403</a></li>
            <li><a href="/error/405">/error/405</a></li>
            <li><a href="/error/418">/error/418</a></li>
        </ul>
    </body>
</html>
'''

@app.route("/error/400")
def error400():
    return "<h1>400 - Bad Request (Некорректный запрос)</h1>", 400

@app.route("/error/401")
def error401():
    return "<h1>401 - Unauthorized (Требуется авторизация)</h1>", 401

@app.route("/error/402")
def error402():
    return "<h1>402 - Payment Required (Требуется оплата)</h1>", 402

@app.route("/error/403")
def error403():
    return "<h1>403 - Forbidden (Доступ запрещен)</h1>", 403

@app.route("/error/405")
def error405():
    return "<h1>405 - Method Not Allowed (Метод не разрещен)</h1>", 405

@app.route("/error/418")
def error418():
    return "<h1>418 - I'm a teapot (Я чайник)</h1>", 418

@app.errorhandler(404)
def not_found(err):
    # Получаем информацию о запросе
    client_ip = request.remote_addr
    access_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    requested_url = request.url
    
    # Добавляем запись в лог
    log_entry = {
        'ip': client_ip,
        'date': access_date,
        'url': requested_url
    }
    error_log.append(log_entry)
    
    # Формируем HTML страницу с ошибкой 404
    return f'''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Страница не найдена (404)</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #212529;
                padding: 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #dc3545;
                text-align: center;
                margin-bottom: 20px;
            }}
            .info {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }}
            .log {{
                background: #e9ecef;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                max-height: 300px;
                overflow-y: auto;
            }}
            .log-entry {{
                margin-bottom: 10px;
                padding: 8px;
                background: white;
                border-radius: 3px;
                border-left: 4px solid #007bff;
            }}
            a {{
                color: #007bff;
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .center {{
                text-align: center;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ОШИБКА 404 - Страница не найдена</h1>
            <img src="https://i.pinimg.com/1200x/48/0f/e9/480fe9f64b6aef3e9675793edcd962a9.jpg" alt="404">
            <div class="info">
                <p><strong>Ваш IP-адрес:</strong> {client_ip}</p>
                <p><strong>Дата и время доступа:</strong> {access_date}</p>
                <p><strong>Запрошенный адрес:</strong> {requested_url}</p>
            </div>
            
            <div class="center">
                <a href="/">Вернуться на главную страницу</a>
            </div>
            
            <div class="log">
                <h3>Лог ошибок 404:</h3>
                {generate_log_html()}
            </div>
        </div>
    </body>
</html>
''', 404

def generate_log_html():
    """Генерирует HTML для отображения лога ошибок"""
    if not error_log:
        return "<p>Лог пуст</p>"
    
    log_html = ""
    for entry in reversed(error_log):  # Показываем последние записи первыми
        log_html += f'''
        <div class="log-entry">
            <strong>IP:</strong> {entry['ip']} | 
            <strong>Дата:</strong> {entry['date']} | 
            <strong>URL:</strong> {entry['url']}
        </div>
        '''
    return log_html

@app.route("/cause_error")
def cause_error():
    return 1/0

@app.errorhandler(500)
def internal_error(err):
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Ошибка 500</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center}}
            h1 {{ color: #212529; }}
        </style>
    </head>
    <body>
        <h1>ОШИБКА 500</h1>
        <p>Произошла внутренняя ошибка!<br></p>
        <a href="/">Главная страница</a>
    </body>
</html>
''', 500

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ['роза', 'тюльпан', 'незабудка', 'ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        return f'''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Цветок #{flower_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .flower-info {{
                background: #e8f4fc;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #3498db;
            }}
            .links {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
                margin-right: 15px;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Информация о цветке</h1>
            
            <div class="flower-info">
                <h2>Цветок #{flower_id}</h2>
                <p><strong>Название:</strong> {flower_list[flower_id]}</p>
                <p><strong>ID цветка:</strong> {flower_id}</p>
                <p><strong>Всего цветов в списке:</strong> {len(flower_list)}</p>
            </div>
            
            <div class="links">
                <a href="/lab2/all_flowers">Посмотреть все цветы</a>
                <a href="/lab2/">Назад к лабораторной 2</a>
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
</html>
'''

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлен новый цветок</h1>
    <p>Название нового цветка: {name} </p>
    <p>Всего цветов: {len(flower_list)}</p>
    <p>Полный список: {flower_list}</p>
    </body>
</html>
'''

@app.route('/lab2/add_flower/')
def add_flower_empty():
    return "вы не задали имя цветка", 400

@app.route('/lab2/all_flowers')
def all_flowers():
    return f'''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Все цветы</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #27ae60;
                padding-bottom: 10px;
            }}
            .stats {{
                background: #d5f4e6;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #27ae60;
            }}
            .flower-list {{
                list-style-type: none;
                padding: 0;
            }}
            .flower-item {{
                background: #f8f9fa;
                margin: 10px 0;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }}
            .flower-id {{
                font-weight: bold;
                color: #2c3e50;
            }}
            .links {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
                margin-right: 15px;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .danger {{
                color: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Список всех цветов</h1>
            
            <div class="stats">
                <h2>Статистика</h2>
                <p><strong>Общее количество цветов:</strong> {len(flower_list)}</p>
            </div>
            
            <h2>Цветы:</h2>
            <ul class="flower-list">
                {"".join([f'<li class="flower-item"><span class="flower-id">#{i}:</span> {flower}</li>' for i, flower in enumerate(flower_list)])}
            </ul>
            
            <div class="links">
                <a href="/lab2/clear_flowers" class="danger">Очистить список цветов</a>
                <a href="/lab2/">Назад к лабораторной 2</a>
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
</html>
'''

@app.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Список цветов очищен</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            h1 {{
                color: #e74c3c;
            }}
            .success {{
                background: #fde8e8;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #e74c3c;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
                margin: 0 10px;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Список цветов очищен!</h1>
            
            <div class="success">
                <p>Все цветы были успешно удалены из списка.</p>
                <p>Текущее количество цветов: 0</p>
            </div>
            
            <div>
                <a href="/lab2/all_flowers">Посмотреть все цветы</a>
                <a href="/lab2/">Назад к лабораторной 2</a>
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
</html>
'''

@app.route('/lab2/example')
def example():
    name, lab_number, group, course = 'Нейверт Арина', 2, 'ФБИ-33', 3
    fruits = [
        {'name': 'яблоки', 'price': 100}, 
        {'name': 'груши', 'price': 120}, 
        {'name': 'апельсины', 'price': 80}, 
        {'name': 'мандарины', 'price': 95}, 
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html',
                           name=name, lab_number=lab_number, group=group,
                           course=course, fruits=fruits)

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных ..."
    return render_template('filter.html', phrase = phrase)

@app.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    # Выполняем математические операции
    operations = {
        'sum': a + b,
        'difference': a - b,
        'product': a * b,
        'quotient': a / b if b != 0 else 'деление на ноль',
        'power': a ** b
    }
    
    return render_template('calc.html', a=a, b=b, operations=operations)

@app.route('/lab2/calc/')
def calc_default():
    """Перенаправляет с /lab2/calc/ на /lab2/calc/1/1"""
    return redirect('/lab2/calc/1/1')

@app.route('/lab2/calc/<int:a>')
def calc_single(a):
    """Перенаправляет с /lab2/calc/a на /lab2/calc/a/1"""
    return redirect(f'/lab2/calc/{a}/1')

# Новый обработчик для отображения списка книг
@app.route('/lab2/books')
def books_list():
    return render_template('books.html', books=books)

# Новый обработчик для отображения коллекции кошек
@app.route('/lab2/cats')
def cats_collection():
    return render_template('cats.html', cats=cats)
