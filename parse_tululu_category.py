import argparse
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from main import check_for_redirect, download_image, download_txt, parse_book_page


def create_parser():
    parser = argparse.ArgumentParser(description='Скачиватель книг по категориям с сайта tululu.org')
    parser.add_argument('-s', '--start_page', default=3,
                        help="С какой страницы начать качать",
                        type=int)
    parser.add_argument('-e', '--end_page', default=4,
                        help="До какой страницы качать",
                        type=int)
    parser.add_argument('--dest_folder', default='catalog/',
                        help="Путь к каталогу с результатами парсинга: "
                             "картинкам, книгам, JSON",
                        type=str)
    parser.add_argument('--skip_imgs',
                        help="не скачивать картинки",)
    parser.add_argument('--skip_txt',
                        help="не скачивать книги",)
    parser.add_argument('--json_path',
                        help="указать свой путь к *.json файлу "
                             "с результатами",
                        type=str)
    return parser


def parse_category_page(start_page, end_page):
    for page in range(start_page, end_page):
        url = f'https://tululu.org/l55/{page}/'
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            book_category_parsed = soup.select('.d_book div.bookimage a')
            book_ids = [book_parsed['href'].strip('/') for book_parsed
                        in book_category_parsed]
            return book_ids
        except requests.exceptions.HTTPError as e:
            print(e)
            print(f"Не удалось спарсить страницу {page}. Страница не найдена")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("Не удалось подключиться к серверу")


def get_books(book_ids, catalog_folder, txt, img):
    bookfolder = f'{catalog_folder}books/'
    Path(bookfolder).mkdir(parents=True, exist_ok=True)
    books = []
    for book_id in book_ids:
        url = f'https://tululu.org/{book_id}/'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(html=response.text, url=url)
            print(f"Название: {book['title']}")
            print(f"Автор: {book['author']}")
            filename = f'{book_id}_{book["title"]}'
            if not txt:
                book['book_path'] = download_txt(url=url,
                                                 filename=filename,
                                                 folder=bookfolder)
            if not img:
                book['img_src'] = download_image(url=book['image_url'],
                                                 folder=f'{catalog_folder}images',
                                                 book_id=book_id)
            books.append(book)
        except requests.exceptions.HTTPError as e:
            print(e)
            print(f"Не удалось скачать книгу {book_id}. Книга не найдена")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("Не удалось подключиться к серверу")
    return books


def make_json_catalog(filename: str, catalog):
    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(catalog, json_file, ensure_ascii=False, sort_keys=True, indent=4)


def main():
    parser = create_parser()
    line_args = parser.parse_args()
    catalog_folder = line_args.dest_folder
    json_path = catalog_folder
    if line_args.json_path:
        json_path = line_args.json_path
    catalog = get_books(book_ids=parse_category_page(start_page=line_args.start_page,
                                                     end_page=line_args.end_page),
                        catalog_folder=catalog_folder,
                        txt=line_args.skip_txt,
                        img=line_args.skip_imgs)
    make_json_catalog(filename=f'{json_path}catalog.json', catalog=catalog)


if __name__ == '__main__':
    main()
