from flask import Flask, url_for, request, redirect, abort, render_template
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
import datetime

app = Flask(__name__)
app.secret_key = 'секретно-секретный секрет'
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)

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
            <li><a href="/lab2">Вторая лабораторная</a></li>
            <li><a href="/lab3">Третья лабораторная</a></li>
            <li><a href="/lab4">Четвертая лабораторная</a></li>
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



@app.errorhandler(404)
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
