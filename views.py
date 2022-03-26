from my_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), names=request.get('names', None))


class About:
    def __call__(self, request):
        return '200 OK', render('another_page.html')


class Examples:
    def __call__(self, request):
        return '200 OK', render('examples.html')


class Contacts:
    def __call__(self, request):
        return '200 OK', render('contact.html')

