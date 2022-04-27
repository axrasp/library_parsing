import os
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def get_book():
    bookfolder = 'books/'
    Path(bookfolder).mkdir(parents=True, exist_ok=True)
    for book_id in range(9, 10):
        url = f'https://tululu.org/b{book_id}/'
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        print(response.status_code)
        try:
            check_for_redirect(response)
            book = get_book_info(url=url)
            filename = f'{book_id}. {book["title"]}'
            #download_txt(url=url, filename=filename, folder='books/')
            download_image(url=book['image_url'], folder='images/')
        except Exception as exc:
            print(exc)


def parse_book_page(url):
    book_comments = {}
    book_genres = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_name_parsed = soup.find('h1').text.split(' \xa0 :: \xa0 ')
    book_image_path = soup.find(class_='bookimage').find('img')['src']
    book_comments_parsed = soup.find_all(class_='texts')
    book_genres_parsed = soup.find_all(title=re.compile("книгам этого жанра"))
    for tag in book_genres_parsed:
        book_genres.append(tag.text)
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
    filename = sanitize_filename(filename)
    file_path = os.path.join(folder, filename)
    with open(f'{file_path}.txt', 'wb') as file:
        file.write(response.content)
    with open(f'{file_path}.txt', 'rb') as file:
        book_text = file.read()
        return book_text


def download_image(url: str, folder: str):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    image_path = unquote(urlsplit(url).path)
    image_name = os.path.basename(image_path)
    print(image_name)
    with open(f'{folder}/{image_name}', 'wb') as file:
        file.write(response.content)


def main():
    get_book()


if __name__ == '__main__':
    main()
