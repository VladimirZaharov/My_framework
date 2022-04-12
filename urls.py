from datetime import date
from views import Index, About, Contacts, Examples, CoursesList, CreateCourse, CreateCategory, CopyCourse, CategoryList
from faker import Faker

fake = Faker()
# front controller

def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    fake = Faker()
    request['names'] = [fake.name() for i in range(10)]


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/about/': About(),
    '/courses/': CoursesList(),
    '/examples/': Examples(),
    '/create-course/': CreateCourse(),
    '/create-category/': CreateCategory(),
    '/copy-course/': CopyCourse(),
    '/category-list/': CategoryList(),
}
