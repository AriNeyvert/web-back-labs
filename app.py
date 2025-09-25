from flask import Flask, url_for, request, redirect, abort, render_template
import datetime

app = Flask(__name__)

# Глобальная переменная для хранения лога 404 ошибок
error_log = []

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
        return "цветок:" + flower_list[flower_id]
    
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

@app.route('/lab2/example')
def example():
    name = 'Арина Нейверт'
    return render_template('example.html', name=name)
