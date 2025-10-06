from flask import Blueprint, url_for, request, redirect
import datetime
lab1 = Blueprint('lab1', __name__)


@lab1.route("/index")
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


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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


@lab1.route("/lab1/image")
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
@lab1.route("/lab1/counter")
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


@lab1.route("/lab1/created")
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


@lab1.route('/lab1/r_counter')
def r_counter():
    global count
    count = 0
    return redirect('/lab1/counter')


@lab1.route('/lab1/')
def lab():
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


@lab1.route("/error/400")
def error400():
    return "<h1>400 - Bad Request (Некорректный запрос)</h1>", 400

@lab1.route("/error/401")
def error401():
    return "<h1>401 - Unauthorized (Требуется авторизация)</h1>", 401

@lab1.route("/error/402")
def error402():
    return "<h1>402 - Payment Required (Требуется оплата)</h1>", 402

@lab1.route("/error/403")
def error403():
    return "<h1>403 - Forbidden (Доступ запрещен)</h1>", 403

@lab1.route("/error/405")
def error405():
    return "<h1>405 - Method Not Allowed (Метод не разрещен)</h1>", 405

@lab1.route("/error/418")
def error418():
    return "<h1>418 - I'm a teapot (Я чайник)</h1>", 418