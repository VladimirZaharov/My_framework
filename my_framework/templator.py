from jinja2 import Template, Environment, FileSystemLoader
from os.path import join


def render(template_name, folder='templates/night_sky_2', **kwargs):
    """
    :param template_name: имя шаблона
    :param folder: папка в которой ищем шаблон
    :param kwargs: параметры
    :return:
    """
    # file_path = join(folder, template_name)
    # # Открываем шаблон по имени
    # with open(file_path, encoding='utf-8') as f:
    #     # Читаем
    #     template = Template(f.read())
    # # рендерим шаблон с параметрами
    # return template.render(**kwargs)

    env = Environment()
    env.loader =FileSystemLoader(folder)
    template = env.get_template(template_name)
    return template.render(**kwargs)
