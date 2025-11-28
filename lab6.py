from flask import Blueprint, render_template, request, session

lab6 = Blueprint('lab6', __name__)

# Инициализация списка офисов с разной стоимостью
offices = []
for i in range(1, 11):
    # Разная стоимость: 900 + остаток от деления на 3
    offices.append({"number": i, "tenant": "", "price": 900 + i % 3 * 100})

@lab6.route('/lab6/')
def main():
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data['id']
    
    # Метод info - получение информации об офисах
    if data['method'] == 'info':
        return {
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }
    
    # Проверка авторизации для методов booking и cancellation
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Не авторизован'
            },
            'id': id
        }
    
    # Метод booking - бронирование офиса
    if data['method'] == 'booking':
        office_number = data['params']
        for office in offices:
            if office['number'] == office_number:
                if office['tenant']:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 2,
                            'message': 'Офис уже забронирован'
                        },
                        'id': id
                    }
                office['tenant'] = login
                return {
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id
                }
    
    # Метод cancellation - снятие аренды
    if data['method'] == 'cancellation':
        office_number = data['params']
        for office in offices:
            if office['number'] == office_number:
                # Проверка: офис должен быть арендован
                if not office['tenant']:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 3,
                            'message': 'Офис не забронирован'
                        },
                        'id': id
                    }
                # Проверка: офис должен быть арендован текущим пользователем
                if office['tenant'] != login:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 4,
                            'message': 'Вы можете отменять только свои бронирования'
                        },
                        'id': id
                    }
                # Снятие аренды
                office['tenant'] = ""
                return {
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id
                }
    
    # Если метод не найден
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Метод не найден'
        },
        'id': id
    }