from flask import Flask, url_for, request, redirect, abort, render_template
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7
from rgz import rgz_bp
import datetime
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно-секретный секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')

# Регистрируем все Blueprints
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(rgz_bp)

# Глобальная переменная для хранения лога 404 ошибок
error_log = []

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

@app.route("/")
@app.route("/index")
def index():
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>НГТУ, ФБ, Лабораторные работы</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                color: #333;
            }
            h1 {
                color: #4a5568;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            .lab-list {
                list-style: none;
                padding: 0;
            }
            .lab-list li {
                margin-bottom: 15px;
            }
            .lab-list a {
                display: block;
                padding: 15px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-weight: bold;
                text-align: center;
            }
            .lab-list a:hover {
                background: #5a67d8;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            .rgz-link {
                background: #ed64a6 !important;
                margin-top: 30px;
                font-size: 1.1em;
            }
            .rgz-link:hover {
                background: #d53f8c !important;
            }
            footer {
                margin-top: 40px;
                text-align: center;
                color: #4a5568;
                font-size: 0.9em;
                border-top: 1px solid #e2e8f0;
                padding-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>НГТУ, ФБ, WEB-программирование, часть 2</h1>
            <h2>Список лабораторных работ</h2>
            <ul class="lab-list">
                <li><a href="/lab1">Первая лабораторная</a></li>
                <li><a href="/lab2">Вторая лабораторная</a></li>
                <li><a href="/lab3">Третья лабораторная</a></li>
                <li><a href="/lab4">Четвертая лабораторная</a></li>
                <li><a href="/lab5">Пятая лабораторная</a></li>
                <li><a href="/lab6">Шестая лабораторная</a></li>
                <li><a href="/lab7">Седьмая лабораторная</a></li>
                <li><a href="/rgz" class="rgz-link">Расчетно-графическое задание: Кинотеатр</a></li>
            </ul>
            <footer>
                <p><strong>Студент:</strong> Нейверт Арина Сергеевна</p>
                <p><strong>Группа:</strong> ФБИ-33</p>
                <p><strong>Курс:</strong> 3</p>
                <p>© 2025 год</p>
            </footer>
        </div>
    </body>
</html>
'''

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
            img {{
                max-width: 300px;
                border-radius: 10px;
                display: block;
                margin: 0 auto;
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
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                text-align: center;
                background: #f8f9fa;
                padding: 50px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ 
                color: #dc3545;
                margin-bottom: 20px;
            }}
            p {{
                color: #6c757d;
                margin-bottom: 30px;
            }}
            a {{
                display: inline-block;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }}
            a:hover {{
                background: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ОШИБКА 500</h1>
            <p>Произошла внутренняя ошибка сервера!</p>
            <p>Пожалуйста, попробуйте позже или обратитесь к администратору.</p>
            <a href="/">Вернуться на главную страницу</a>
        </div>
    </body>
</html>
''', 500

if __name__ == '__main__':
    app.run(debug=True)