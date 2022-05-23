from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import more_itertools


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open('catalog/catalog.json', 'rb') as file:
        catalog = json.load(file)
        catalog_chunked = list(more_itertools.chunked(catalog, 2))
        print(len(catalog_chunked))
    rendered_page = template.render(
        catalog=catalog,
        catalog_chunked=catalog_chunked
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


server = Server()
server.watch('template.html', on_reload)
server.serve(root='docs/_build/html')