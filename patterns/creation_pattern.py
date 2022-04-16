from copy import deepcopy
from quopri import decodestring


# абстрактный пользователь
from sqlite3 import connect

from patterns.architectural_system_pattern_unit_of_work import DomainObject


class User:
    def __init__(self, first_name, last_name, login, password):
        self.first_name = first_name
        self.last_name = last_name
        self.login = login
        self.password = password
        self.courses = []


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User, DomainObject):
    auto_id = 0
    
    def __init__(self, first_name, last_name, login, password):
        super().__init__(first_name, last_name, login, password)
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


class StudentMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'student'

    def all(self):
        statement = f'SELECT id, first_name, last_name, login, password from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, first_name, last_name, login, password = item
            student = Student(first_name, last_name, login, password)
            student.id = id
            result.append(student)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, first_name, last_name, login, password FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Student(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (first_name, last_name, login, password) VALUES (?,?,?,?)"
        self.cursor.execute(statement, (obj.first_name, obj.last_name, obj.login, obj.password))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET (first_name=?, last_name=?, login=?, password=?) WHERE id=?"

        self.cursor.execute(statement, (obj.first_name, obj.last_name, obj.login, obj.password, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'student': StudentMapper,
        #'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Student):

            return StudentMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')