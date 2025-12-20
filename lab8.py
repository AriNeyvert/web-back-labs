from flask import Blueprint, render_template

lab8 = Blueprint('lab8', __name__, 
                 template_folder='templates/lab8',
                 static_folder='static/lab8')

@lab8.route('/lab8/')
@lab8.route('/index')
def index():
    return render_template('lab8/index.html', username="anonymous")

@lab8.route('/login')
def login():
    return "Страница входа (заготовка)"

@lab8.route('/register')
def register():
    return "Страница регистрации (заготовка)"

@lab8.route('/articles')
def articles():
    return "Список статей (заготовка)"

@lab8.route('/create')
def create():
    return "Создание статьи (заготовка)"