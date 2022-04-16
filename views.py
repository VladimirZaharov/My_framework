from my_framework.templator import render
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork
from patterns.creation_pattern import Engine, Logger, UserFactory, MapperRegistry
from patterns.structure_patterns import AppRouter, Debug


site = Engine()
logger = Logger('main')
decorator_routes = {}
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

class Index:
    # @Debug
    def __call__(self, request):
        return '200 OK', render('index.html', date=request.get('date', None), names=request.get('names', None))


class About:
    # @Debug
    def __call__(self, request):
        return '200 OK', render('another_page.html')


class Examples:
    # @Debug
    def __call__(self, request):
        return '200 OK', render('examples.html')


@AppRouter(route=decorator_routes, url='/contact/')
class Contacts:
    # @Debug
    def __call__(self, request):
        return '200 OK', render('contact.html')


@AppRouter(route=decorator_routes, url='/students/')
class StudentsList:
    def __call__(self, request):
        logger.log('Список студентов')
        return '200 OK', render('students.html', objects_list=site.students)


@AppRouter(route=decorator_routes, url='/student-registration/')
class CreateStudent:
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            first_name, last_name, login, password = data['first_name'], data['last_name'], data['login'], data['password']
            student = site.create_user('student', first_name, last_name, login, password)
            site.students.append(student)
            student.mark_new()
            UnitOfWork.get_current().commit()
            return '200 OK', render('student.html', object=student, objects_list=site.courses)
        else:
            return '200 OK', render('student_registration.html')


@AppRouter(route=decorator_routes, url='/student-login/')
class LoginStudent:
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            login = data['login']
            password = data['password']
            login = site.decode_value(login)
            password = site.decode_value(password)
            for student in site.students:
                if login == site.students.login:
                    if password == site.students.password:
                        return '200 OK', render('student.html', object=student, objects_list=site.courses)
                return '200 OK', render('students.html')
        else:
            return '200 OK', render('student_login.html')


@AppRouter(route=decorator_routes, url='/add-course-to-student/')
class RegisterForCourse:
    def __call__(self, request):
        student_id = int(request['request_params']['id'])
        for s in site.students:
            if s.id == student_id:
                if request['method'] == 'POST':
                    data = request['data']
                    courses = data['courses_to_register']
                    for course in courses:
                        if course not in s.courses:
                            s.courses.append(course)
                    return '200 OK', render('course_register.html', object=s, objects_list=site.courses)
                else:
                    return '200 OK', render('course_register.html', object=s, objects_list=site.courses)


# контроллер - список курсов
class CoursesList:
    def __call__(self, request):
        logger.log('Список курсов')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('courses.html',
                                    objects_list=category.courses,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - создать курс
class CreateCourse:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                course = site.create_course('record', name, category)
                site.courses.append(course)

            return '200 OK', render('courses.html',
                                    objects_list=category.courses,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_course.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('course_categories.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


# контроллер - список категорий
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('course_categories.html',
                                objects_list=site.categories)


# контроллер - копировать курс
class CopyCourse:
    # @Debug
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_course = site.get_course(name)
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                site.courses.append(new_course)

            return '200 OK', render('courses.html',
                                    objects_list=site.courses,
                                    name=new_course.category.name)
        except KeyError:
            return '200 OK', 'No courses have been added yet'
