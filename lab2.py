from flask import Blueprint, request, redirect, render_template, abort
lab2 = Blueprint('lab2', __name__)


# Список книг для отображения
books = [
    {'author': 'Фёдор Достоевский', 'title': 'Преступление и наказание', 'genre': 'Роман', 'pages': 671},
    {'author': 'Лев Толстой', 'title': 'Война и мир', 'genre': 'Роман-эпопея', 'pages': 1225},
    {'author': 'Михаил Булгаков', 'title': 'Мастер и Маргарита', 'genre': 'Роман', 'pages': 480},
    {'author': 'Антон Чехов', 'title': 'Рассказы', 'genre': 'Рассказ', 'pages': 350},
    {'author': 'Александр Пушкин', 'title': 'Евгений Онегин', 'genre': 'Роман в стихах', 'pages': 240},
    {'author': 'Николай Гоголь', 'title': 'Мёртвые души', 'genre': 'Поэма', 'pages': 352},
    {'author': 'Иван Тургенев', 'title': 'Отцы и дети', 'genre': 'Роман', 'pages': 288},
    {'author': 'Александр Дюма', 'title': 'Граф Монте-Кристо', 'genre': 'Приклюденческий роман', 'pages': 928},
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

# Обновленный список цветов с ценами
flower_list = [
    {'name': 'роза', 'price': 300},
    {'name': 'тюльпан', 'price': 310},
    {'name': 'незабудка', 'price': 320},
    {'name': 'ромашка', 'price': 330},
    {'name': 'георгин', 'price': 300},
    {'name': 'гладиолус', 'price': 310}
]

@lab2.route('/lab2/a')
def a():
    return 'без слэша'

@lab2.route('/lab2/a/')
def a2():
    return 'со слэшем'

@lab2.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        flower = flower_list[flower_id]
        return render_template('flower_detail.html', 
                             flower_id=flower_id, 
                             flower=flower,
                             total_flowers=len(flower_list))

# Новый обработчик для добавления цветка через форму
@lab2.route('/lab2/add_flower', methods=['GET', 'POST'])
def add_flower():
    if request.method == 'POST':
        flower_name = request.form.get('name')
        if flower_name:
            # Добавляем цветок с ценой по умолчанию 300 руб
            flower_list.lab2end({'name': flower_name, 'price': 300})
        return redirect('/lab2/all_flowers')
    else:
        # Если GET-запрос, показываем форму
        return render_template('add_flower.html')

@lab2.route('/lab2/add_flower/<name>')
def add_flower_by_url(name):
    # Добавляем цветок с ценой по умолчанию 300 руб
    flower_list.lab2end({'name': name, 'price': 300})
    return redirect('/lab2/all_flowers')

# Новый обработчик для удаления цветка по номеру
@lab2.route('/lab2/del_flower/<int:flower_id>')
def del_flower(flower_id):
    if flower_id < 0 or flower_id >= len(flower_list):
        abort(404)
    
    # Удаляем цветок из списка
    flower_list.pop(flower_id)
    
    # Перенаправляем обратно на страницу всех цветов
    return redirect('/lab2/all_flowers')

@lab2.route('/lab2/all_flowers')
def all_flowers():
    return render_template('all_flowers.html', flowers=flower_list)

@lab2.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return redirect('/lab2/all_flowers')

@lab2.route('/lab2/example')
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

@lab2.route('/lab2/')
def lab():
    return render_template('lab2.html')

@lab2.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных ..."
    return render_template('filter.html', phrase = phrase)

@lab2.route('/lab2/calc/<int:a>/<int:b>')
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

@lab2.route('/lab2/calc/')
def calc_default():
    """Перенаправляет с /lab2/calc/ на /lab2/calc/1/1"""
    return redirect('/lab2/calc/1/1')

@lab2.route('/lab2/calc/<int:a>')
def calc_single(a):
    """Перенаправляет с /lab2/calc/a на /lab2/calc/a/1"""
    return redirect(f'/lab2/calc/{a}/1')

@lab2.route('/lab2/books')
def books_list():
    return render_template('books.html', books=books)

@lab2.route('/lab2/cats')
def cats_collection():
    return render_template('cats.html', cats=cats)

