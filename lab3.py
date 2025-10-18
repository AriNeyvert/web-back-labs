from flask import Blueprint, render_template, request, make_response, redirect
from datetime import datetime

lab3 = Blueprint('lab3', __name__)

# Список товаров (смартфоны)
products = [
    {"id": 1, "name": "iPhone 15 Pro", "brand": "Apple", "price": 99990, "color": "Титановый", "storage": "128GB"},
    {"id": 2, "name": "Samsung Galaxy S24", "brand": "Samsung", "price": 79990, "color": "Черный", "storage": "256GB"},
    {"id": 3, "name": "Xiaomi 14", "brand": "Xiaomi", "price": 59990, "color": "Белый", "storage": "256GB"},
    {"id": 4, "name": "Google Pixel 8 Pro", "brand": "Google", "price": 89990, "color": "Серый", "storage": "128GB"},
    {"id": 5, "name": "OnePlus 12", "brand": "OnePlus", "price": 64990, "color": "Зеленый", "storage": "256GB"},
    {"id": 6, "name": "iPhone 14", "brand": "Apple", "price": 69990, "color": "Синий", "storage": "128GB"},
    {"id": 7, "name": "Samsung Galaxy A54", "brand": "Samsung", "price": 34990, "color": "Фиолетовый", "storage": "128GB"},
    {"id": 8, "name": "Xiaomi Redmi Note 13", "brand": "Xiaomi", "price": 24990, "color": "Черный", "storage": "128GB"},
    {"id": 9, "name": "Realme 11 Pro+", "brand": "Realme", "price": 32990, "color": "Золотой", "storage": "256GB"},
    {"id": 10, "name": "Nothing Phone 2", "brand": "Nothing", "price": 45990, "color": "Белый", "storage": "128GB"},
    {"id": 11, "name": "iPhone 15 Pro Max", "brand": "Apple", "price": 129990, "color": "Титановый", "storage": "256GB"},
    {"id": 12, "name": "Samsung Galaxy Z Flip5", "brand": "Samsung", "price": 99990, "color": "Сиреневый", "storage": "256GB"},
    {"id": 13, "name": "Google Pixel 7a", "brand": "Google", "price": 44990, "color": "Голубой", "storage": "128GB"},
    {"id": 14, "name": "Xiaomi Poco X6 Pro", "brand": "Xiaomi", "price": 29990, "color": "Желтый", "storage": "256GB"},
    {"id": 15, "name": "Sony Xperia 5 V", "brand": "Sony", "price": 79990, "color": "Черный", "storage": "128GB"},
    {"id": 16, "name": "Motorola Edge 40", "brand": "Motorola", "price": 39990, "color": "Зеленый", "storage": "256GB"},
    {"id": 17, "name": "Honor Magic 5 Pro", "brand": "Honor", "price": 59990, "color": "Бирюзовый", "storage": "512GB"},
    {"id": 18, "name": "iPhone SE 2022", "brand": "Apple", "price": 42990, "color": "Красный", "storage": "64GB"},
    {"id": 19, "name": "Samsung Galaxy S23 FE", "brand": "Samsung", "price": 54990, "color": "Кремовый", "storage": "128GB"},
    {"id": 20, "name": "Xiaomi 13T", "brand": "Xiaomi", "price": 49990, "color": "Черный", "storage": "256GB"}
]

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


@lab3.route('/lab3/del_settings_cookies')
def del_settings_cookies():
    """Очистка всех кук, установленных в настройках"""
    resp = make_response(redirect('/lab3/settings'))
    # Удаляем все куки, связанные с настройками
    resp.delete_cookie('color')
    resp.delete_cookie('bgcolor')
    resp.delete_cookie('fontsize')
    resp.delete_cookie('fontstyle')
    return resp


@lab3.route('/lab3/ticket')
def ticket_form():
    return render_template('lab3/ticket_form.html')


@lab3.route('/lab3/ticket_result')
def ticket_result():
    # Получаем данные из формы
    fio = request.args.get('fio')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    age_str = request.args.get('age')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')

    errors = {}
    
    # Проверка на пустые поля
    if not fio:
        errors['fio'] = 'Заполните поле ФИО пассажира'
    if not shelf:
        errors['shelf'] = 'Выберите полку'
    if not age_str:
        errors['age'] = 'Заполните поле возраста'
    if not departure:
        errors['departure'] = 'Заполните пункт выезда'
    if not destination:
        errors['destination'] = 'Заполните пункт назначения'
    if not date:
        errors['date'] = 'Заполните дату поездки'

    # Проверка возраста
    if age_str:
        try:
            age = int(age_str)
            if age < 1 or age > 120:
                errors['age'] = 'Возраст должен быть от 1 до 120 лет'
        except ValueError:
            errors['age'] = 'Возраст должен быть числом'

    # Если есть ошибки, показываем форму снова
    if errors:
        return render_template('lab3/ticket_form.html', errors=errors,
                             fio=fio, shelf=shelf, linen=linen, baggage=baggage,
                             age=age_str, departure=departure, destination=destination,
                             date=date, insurance=insurance)

    age = int(age_str)
    
    # Расчет стоимости билета
    if age < 18:
        base_price = 700  # детский билет
        ticket_type = "Детский билет"
    else:
        base_price = 1000  # взрослый билет
        ticket_type = "Взрослый билет"

    total_price = base_price

    # Доплаты
    if shelf in ['lower', 'lower-side']:
        total_price += 100  # за нижнюю полку
    
    if linen == 'on':
        total_price += 75  # за бельё
    
    if baggage == 'on':
        total_price += 250  # за багаж
    
    if insurance == 'on':
        total_price += 150  # за страховку

    # Преобразуем значения для отображения
    linen_display = "Да" if linen == 'on' else "Нет"
    baggage_display = "Да" if baggage == 'on' else "Нет"
    insurance_display = "Да" if insurance == 'on' else "Нет"

    # Отображаем тип полки
    shelf_display = {
        'lower': 'Нижняя',
        'upper': 'Верхняя', 
        'upper-side': 'Верхняя боковая',
        'lower-side': 'Нижняя боковая'
    }.get(shelf, shelf)

    return render_template('lab3/ticket_result.html',
                         fio=fio,
                         shelf=shelf_display,
                         linen=linen_display,
                         baggage=baggage_display,
                         age=age,
                         departure=departure,
                         destination=destination,
                         date=date,
                         insurance=insurance_display,
                         ticket_type=ticket_type,
                         total_price=total_price)


@lab3.route('/lab3/products')
def products_page():
    # Получаем минимальную и максимальную цену из всех товаров
    min_price_all = min(product['price'] for product in products)
    max_price_all = max(product['price'] for product in products)
    
    # Получаем значения из формы
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    # Обработка кнопки сброса
    if request.args.get('reset'):
        resp = make_response(redirect('/lab3/products'))
        resp.delete_cookie('products_min_price')
        resp.delete_cookie('products_max_price')
        return resp
    
    # Если форма отправлена, сохраняем значения в куки
    if min_price is not None or max_price is not None:
        resp = make_response(redirect('/lab3/products'))
        if min_price:
            resp.set_cookie('products_min_price', min_price)
        else:
            resp.delete_cookie('products_min_price')
        if max_price:
            resp.set_cookie('products_max_price', max_price)
        else:
            resp.delete_cookie('products_max_price')
        return resp
    
    # Если форма не отправлена, берем значения из куки
    min_price = request.cookies.get('products_min_price')
    max_price = request.cookies.get('products_max_price')
    
    # Фильтрация товаров
    filtered_products = products
    
    if min_price or max_price:
        try:
            min_val = float(min_price) if min_price else min_price_all
            max_val = float(max_price) if max_price else max_price_all
            
            # Если пользователь перепутал min и max, меняем их местами
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            
            filtered_products = [
                product for product in products
                if min_val <= product['price'] <= max_val
            ]
        except ValueError:
            # Если введены некорректные значения, показываем все товары
            filtered_products = products
    
    return render_template('lab3/products.html',
                         products=filtered_products,
                         min_price=min_price,
                         max_price=max_price,
                         min_price_all=min_price_all,
                         max_price_all=max_price_all,
                         products_count=len(filtered_products),
                         all_products_count=len(products))


@lab3.route('/lab3/products_reset')
def products_reset():
    """Очистка фильтров и показ всех товаров"""
    resp = make_response(redirect('/lab3/products'))
    resp.delete_cookie('products_min_price')
    resp.delete_cookie('products_max_price')
    return resp
