import json
import os.path
from pathlib import Path

import more_itertools
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def on_reload():
    pages_folder = 'pages'
    books_per_page = 10
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open('catalog/catalog.json', 'rb') as file:
        catalog = json.load(file)
    catalog_page_split = list(more_itertools.chunked(catalog, books_per_page))
    page_qty = len(catalog_page_split)
    page_indices = list(range(1, (len(catalog_page_split))+1))
    for i, catalog_page in enumerate(catalog_page_split, 1):
        catalog_column_split = list(more_itertools.chunked(catalog_page, 2))
        rendered_page = template.render(
            page_number=i,
            page_indices=page_indices,
            page_qty=page_qty,
            catalog=catalog_page,
            catalog_chunked=catalog_column_split
        )
        page_name = f'index{i}.html'
        page_path = os.path.join(pages_folder, page_name)
        with open(page_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='docs/_build/html')


if __name__ == '__main__':
    main()
