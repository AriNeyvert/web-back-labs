
from flask import Flask, Blueprint, render_template

app = Flask(__name__)

# Создаем Blueprint для lab5
lab5 = Blueprint('lab5', __name__, template_folder='templates', static_folder='static')

@lab5.route('/lab5/')
def index():
    # Пока используем "anonymous" как имя пользователя по умолчанию
    username = "Anonymous"
    return render_template('lab5/lab5.html', username=username)

@lab5.route('/lab5/login')
def login():
    return "Страница входа"

@lab5.route('/lab5/register')
def register():
    return "Страница регистрации"

@lab5.route('/lab5/list')
def list_articles():
    return "Список статей"

@lab5.route('/lab5/create')
def create_article():
    return "Создать статью"
