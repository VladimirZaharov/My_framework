from time import time


class AppRouter:
    def __init__(self, route, url):
        self.route = route
        self.url = url

    def __call__(self, cls):
        self.route[self.url] = cls()


# структурный паттерн - Декоратор
class Debug:

    def __init__(self, name):

        self.name = name

    def __call__(self, cls):
        '''
        сам декоратор
        '''

        # это вспомогательная функция будет декорировать каждый отдельный метод класса, см. ниже
        def timeit(method):
            '''
            нужен для того, чтобы декоратор класса wrapper обернул в timeit
            каждый метод декорируемого класса
            '''
            def timed(*args, **kwargs):
                ts = time()
                result = method(*args, **kwargs)
                te = time()
                delta = te - ts

                print(f'debug --> {self.name} выполнялся {delta:2.2f} ms')
                return result

            return timed

        return timeit(cls)
