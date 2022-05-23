import argparse
import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_parser():
    parser = argparse.ArgumentParser(description='Скачиватель книг '
                                                 'с сайта tululu.org')
    parser.add_argument('-s', '--start_id', default=4,
                        help="С какого номера книги начать",
                        type=int)
    parser.add_argument('-e', '--end_id', default=5,
                        help="Да какого номера закончить",
                        type=int)
    parser.add_argument('--dest_folder', default='',
                        help="Путь к папке с книгами и "
                             "картинкам",
                        type=str)
    return parser


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def get_book(start_id: int, end_id: int, catalog_folder):
    bookfolder = f'{catalog_folder}books/'
    Path(bookfolder).mkdir(parents=True, exist_ok=True)
    for book_id in range(start_id, end_id):
        url = f'https://tululu.org/txt.php?id={book_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(html=response.text, url=url)
            filename = f'{book_id}. {book["title"]}'
            download_txt(url=url, filename=filename, folder=bookfolder)
            download_image(url=book['image_url'],
                           folder=f'{catalog_folder}images/',
                           book_id=book_id)
        except requests.exceptions.HTTPError as e:
            print(e)
        except requests.exceptions.ConnectionError as e:
            print(e)


def parse_book_page(html, url):
    book_comments = {}
    soup = BeautifulSoup(html, 'lxml')
    book_name_parsed = soup.select_one('h1').get_text().split(' \xa0 :: \xa0 ')
    book_image_path = soup.select_one('.bookimage img')['src']
    book_comments_parsed = soup.select('.texts')
    book_genres_parsed = soup.select('[title~="жанра"]')
    book_genres = [tag.text for tag in book_genres_parsed]
    for comment in book_comments_parsed:
        name = comment.select_one('b').get_text()
        comment = comment.select_one('.black').get_text()
        book_comments[name] = comment
    book_image_url = urljoin(url, book_image_path)
    book = dict(zip(['title', 'author'], book_name_parsed))
    book['image_url'] = book_image_url
    book['comments'] = book_comments
    book['genre'] = book_genres
    return book


def download_txt(url: str, filename: str, folder: str):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = sanitize_filename(filename)
    file_path = os.path.join(folder, filename)
    with open(f'{file_path}.txt', 'w') as file:
        file.write(response.text)
    return f'{file_path}.txt'


def download_image(url: str, folder: str, book_id: int):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    image_url_unquoted = unquote(urlsplit(url).path)
    image_name = f'b{book_id}_{os.path.basename(image_url_unquoted)}'
    image_path = os.path.join(folder, image_name)
    with open(image_path, 'wb') as file:
        file.write(response.content)
    return image_path


def main():
    parser = create_parser()
    line_args = parser.parse_args()
    get_book(start_id=line_args.start_id,
             end_id=line_args.end_id,
             catalog_folder=line_args.dest_folder)


if __name__ == '__main__':
    main()
