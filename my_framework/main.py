
class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Framework:

    """Класс Framework - основа фреймворка"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        # получаем адрес, по которому выполнен переход
        path = environ['PATH_INFO']
        # print(environ)
        # добавление закрывающего слеша
        if not path.endswith('/'):
            path = f'{path}/'
        print(self.parse_data(environ))
        # находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()
        request = {}
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts_lst:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    def parse_data(self, env):
        data_len = int(env['CONTENT_LENGTH']) if env['CONTENT_LENGTH'] else 0
        data = env['wsgi.input'].read(data_len) if data_len > 0 else b''
        data = data.decode('utf-8')
        if data:
            items = data.split('&')
            dict_items = {item.split('=')[0]: item.split('=')[1] for item in items}
            return dict_items
        return 'no data'