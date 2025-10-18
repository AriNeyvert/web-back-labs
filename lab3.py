from flask import Blueprint, render_template, request, make_response, redirect
from datetime import datetime
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age')
    
    if name is None:
        name = "Аноним"
    
    if age is None:
        age = "не указан"
    
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Arina', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'

    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'

    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)

@lab3.route('/lab3/order')
def order():
    return render_template('/lab3/order.html')

@lab3.route('/lab3/pay')
def pay():
    price=0
    drink = request.args.get('drink')
    # Пусть кофе стоит 120 рублей, черный чай - 80 рублей, зеленый - 70 рублей
    if drink == 'cofee':
        price = 120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70

    # Добавка молока удорожает напиток на 30 рублей, а сахара - на 10
    if request.args.get('milk') == 'on':
        price +=30
    if request.args.get('sugar') == 'on':
        price +=10

    return render_template('lab3/pay.html', price=price)

@lab3.route('/lab3/success', methods=['POST'])
def success():
    price = request.form.get('price', 0)
    return render_template('lab3/success.html', 
                         price=price,
                         drink_name=request.form.get('drink_name', ''),
                         additions=request.form.get('additions', '').split(',') if request.form.get('additions') else [],
                         order_time=datetime.now().strftime("%H:%M %d.%m.%Y"))

@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bgcolor = request.args.get('bgcolor')
    fontsize = request.args.get('fontsize')
    fontstyle = request.args.get('fontstyle')

    # если пришли параметры — сохраняем их в cookies
    if color or bgcolor or fontsize or fontstyle:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bgcolor:
            resp.set_cookie('bgcolor', bgcolor)
        if fontsize:
            resp.set_cookie('fontsize', fontsize)
        if fontstyle:
            resp.set_cookie('fontstyle', fontstyle)
        return resp

    # если параметров нет — берём из cookies
    color = request.cookies.get('color')
    bgcolor = request.cookies.get('bgcolor')
    fontsize = request.cookies.get('fontsize')
    fontstyle = request.cookies.get('fontstyle')

    resp = make_response(render_template(
        'lab3/settings.html',
        color=color,
        bgcolor=bgcolor,
        fontsize=fontsize,
        fontstyle=fontstyle
    ))
    return resp
