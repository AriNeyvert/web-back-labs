from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

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
</html>
'''

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

@app.errorhandler(404)
def not_found(err):
    return "нет такой страницы", 404

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
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Страница не найдена (404)</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f8f9fa;
                color: #212529;
                text-align: center;
                padding: 50px 20px;
                line-height: 1.6;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            p {
                font-size: 18px;
                margin-bottom: 1.5rem;
            }
            a {
                color: #2980b9;
                text-decoration: none;
                font-weight: 500;
            }
            a:hover {
                text-decoration: underline;
            }
            ul {
                list-style: none;
                padding: 0;
                text-align: left;
                display: inline-block;
            }
            li {
                margin-bottom: 10px;
                padding-left: 1em;
            }
            li:before {
                content: "•";
                color: #2980b9;
                display: inline-block;
                width: 1em;
                margin-left: -1em;
            }
            footer {
                margin-top: 40px;
                font-size: 14px;
                color: #6c757d;
            }
        </style>
    </head>
    <body>
        <h1>ОШИБКА 404!!!</h1>
        <p>Невозможно найти страницу :(</p>
        <a href="/">Главная страница</a>
        <br>
        <img src="https://i.pinimg.com/1200x/48/0f/e9/480fe9f64b6aef3e9675793edcd962a9.jpg" alt="404">
    </body>
</html>
''',404

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
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center}
            h1 { color: #212529; }
        </style>
    </head>
    <body>
        <h1>ОШИБКА 500</h1>
        <p>Произошла внутренняя ошибка!<br></p>
        <a href="/">Главная страница</a>
    </body>
</html>
''', 500
