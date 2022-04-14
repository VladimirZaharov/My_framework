from copy import deepcopy
from quopri import decodestring


# абстрактный пользователь
class User:
    def __init__(self, first_name, last_name, login, user_password):
        self.first_name = first_name
        self.last_name = last_name
        self.login = login
        self.user_password = user_password
        self.courses = []


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User):
    auto_id = 0
    
    def __init__(self, first_name, last_name, login, user_password):
        super().__init__(first_name, last_name, login, user_password)
        self.id = Student.auto_id
        Student.auto_id += 1
        
    def add_course(self, course):
        self.courses.append(course)


class UserFactory:
    @staticmethod
    def create(type_, first_name, last_name, login, password):
        types = {
            'student': Student,
            'teacher': Teacher
        }
        return types[type_](first_name, last_name, login, password)


# порождающий паттерн Прототип
class CoursePrototype:
    # прототип курсов обучения

    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.courses.append(self)


# интерактивный курс
class InteractiveCourse(Course):
    pass


# курс в записи
class RecordCourse(Course):
    pass


class CourseFactory:
    @staticmethod
    def create(type_, name, category):
        types = {
            'interactive': InteractiveCourse,
            'record': RecordCourse
        }
        return types[type_](name, category)


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.courses = []

    def course_count(self):
        result = len(self.courses)
        if self.category:
            result += self.category.course_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []

    @staticmethod
    def create_user(type_, first_name, last_name, login, password):
        return UserFactory.create(type_, first_name, last_name, login, password)

    def add_course_to_student(self, student_id, course):
        for student in self.students:
            if student_id == student.id:
                student.add_course(course) 

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_course(type_, name, category):
        return CourseFactory.create(type_, name, category)

    def get_course(self, name):
        for item in self.courses:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)


class FileLogger(Logger):

    @staticmethod
    def log(text):
        with open('log.txt', 'a', encoding='utf-8') as l:
            l.writelines(text)
