import argparse
import os
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_id', default=1,
                        help="С какого номера книги начать",
                        type=int)
    parser.add_argument('-e', '--end_id', default=5,
                        help="Да какого номера закончить",
                        type=int)
    return parser


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def get_book(start_id: str, end_id: str):
    bookfolder = 'books/'
    Path(bookfolder).mkdir(parents=True, exist_ok=True)
    for book_id in range(start_id, end_id):
        url = f'https://tululu.org/b{book_id}/'
        for i in range(3):
            try:
                response = requests.get(url)
                response.raise_for_status()
                break
            except requests.exceptions.ConnectionError as e:
                print(e)
                print(f"Не удалось скачать книгу {book_id}. "
                      f"Ошибка подключения. "
                      f"Повторное подключение к серверу {3-i}")
                time.sleep(5)
            except requests.exceptions.HTTPError as e:
                print(e)
                print(f"Не удалось скачать книгу {book_id}. Книга не найдена")
                break
        try:
            check_for_redirect(response)
            book = parse_book_page(html=response.text, url=url)
            print(f"Название: {book['title']}")
            print(f"Автор: {book['author']}")
            filename = f'{book_id}. {book["title"]}'
            download_txt(url=url, filename=filename, folder='books/')
            download_image(url=book['image_url'], folder='images/')

        except requests.exceptions.HTTPError as e:
            print(e)
            print(f"Не удалось скачать книгу {book_id}. Книга не найдена")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("Не удалось подключиться к серверу")


def parse_book_page(html, url):
    book_comments = {}
    soup = BeautifulSoup(html, 'lxml')
    book_name_parsed = soup.find('h1').text.split(' \xa0 :: \xa0 ')
    book_image_path = soup.find(class_='bookimage').find('img')['src']
    book_comments_parsed = soup.find_all(class_='texts')
    book_genres_parsed = soup.find_all(title=re.compile("книгам этого жанра"))
    book_genres = [tag.text for tag in book_genres_parsed]
    for comment in book_comments_parsed:
        name = comment.find('b').text
        comment = comment.find(class_='black').text
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
    with open(f'{file_path}.txt', 'wb') as file:
        file.write(response.content)


def download_image(url: str, folder: str):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    image_path = unquote(urlsplit(url).path)
    image_name = os.path.basename(image_path)
    with open(f'{folder}/{image_name}', 'wb') as file:
        file.write(response.content)


def main():
    parser = create_parser()
    line_args = parser.parse_args()
    get_book(start_id=line_args.start_id, end_id=line_args.end_id)


if __name__ == '__main__':
    main()
