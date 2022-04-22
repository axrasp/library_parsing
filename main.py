import requests
from pathlib import Path


def main():
    bookfolder = 'books'
    Path(bookfolder).mkdir(parents=True, exist_ok=True)
    for book_id in range(1, 10):
        url = f'https://tululu.org/txt.php?id={book_id}'
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        filename = f"book{book_id}.txt"
        with open(f'{bookfolder}/{filename}', 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main ()
