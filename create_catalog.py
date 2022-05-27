import argparse
import json
from pathlib import Path
import os.path

import requests
from bs4 import BeautifulSoup

from get_book_by_id import (check_for_redirect, download_image, download_txt,
                            parse_book_page)


def create_parser():
    parser = argparse.ArgumentParser(description='Скачиватель книг по '
                                                 'категориям '
                                                 'с сайта tululu.org')
    parser.add_argument('-s', '--start_page', default=3,
                        help="С какой страницы начать качать",
                        type=int)
    parser.add_argument('-e', '--end_page', default=4,
                        help="До какой страницы качать",
                        type=int)
    parser.add_argument('--dest_folder', default='catalog',
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


def get_book_ids(start_page, end_page):
    book_ids = []
    for page in range(start_page, end_page):
        url = f'https://tululu.org/l55/{page}/'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_category_parsed = soup.select('.d_book div.bookimage a')
            book_id = [book_parsed['href'].strip('/b') for book_parsed
                        in book_category_parsed]
            book_ids.extend(book_id)
        except requests.exceptions.HTTPError as e:
            print(e)
        except requests.exceptions.ConnectionError as e:
            print(e)
    return book_ids


def get_books(book_ids, catalog_folder, skip_txt, skip_img):
    book_folder = os.path.join(catalog_folder, 'books')
    images_folder = os.path.join(catalog_folder, 'images')
    Path(book_folder).mkdir(parents=True, exist_ok=True)
    books = []
    for book_id in book_ids:
        url = f'https://tululu.org/b{book_id}/'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(html=response.text, url=url)
            filename = f'b{book_id}_{book["title"]}'
            if not skip_txt:
                url_txt = f'https://tululu.org/txt.php?id={book_id}'
                book['book_path'] = download_txt(url=url_txt,
                                                 filename=filename,
                                                 folder=book_folder)
            if not skip_img:
                book['img_src'] = download_image(
                    url=book['image_url'],
                    folder=images_folder,
                    book_id=book_id
                )
            books.append(book)
        except requests.exceptions.HTTPError as e:
            print(e)
        except requests.exceptions.ConnectionError as e:
            print(e)
    return books


def main():
    parser = create_parser()
    line_args = parser.parse_args()
    catalog_folder = line_args.dest_folder
    json_path = Path.cwd() / catalog_folder / 'catalog.json'
    if line_args.json_path:
        json_path = line_args.json_path
    book_ids = get_book_ids(start_page=line_args.start_page,
                            end_page=line_args.end_page)
    catalog = get_books(book_ids=book_ids,
                        catalog_folder=catalog_folder,
                        skip_txt=line_args.skip_txt,
                        skip_img=line_args.skip_imgs)
    with open(json_path, 'w', encoding='utf8') as json_file:
        json.dump(catalog, json_file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=4)


if __name__ == '__main__':
    main()
