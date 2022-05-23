import os.path

from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import more_itertools
from pathlib import Path


def on_reload(page_folder):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open('catalog/catalog.json', 'rb') as file:
        catalog = json.load(file)
        catalog_page_split = list(more_itertools.chunked(catalog, 10))
        print(len(catalog_page_split))
        i = 1
    for catalog_page in catalog_page_split:
        catalog_column_split = list(more_itertools.chunked(catalog_page, 2))
        rendered_page = template.render(
            catalog=catalog_page,
            catalog_chunked=catalog_column_split
        )
        page_name = f'index{i}.html'
        page_path = os.path.join(page_folder, page_name)
        with open(page_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)
        i += 1


def main():
    page_folder = 'pages'
    Path(page_folder).mkdir(parents=True, exist_ok=True)
    on_reload(page_folder=page_folder)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='docs/_build/html')


if __name__ == '__main__':
    main()