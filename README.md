# Скачиватель электронных книг со своей библиотекой 

Код позволяет скачивать книги, описанием к ним и обложки с сайта https://tululu.org/.

## Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

## Запуск скрипта для скачивания конкретной книги

Запуск скрипта производится командой

```
python3 main.py 
```

Возможно добавить дополнительные аргументы, для того, чтобы скачивать книги с определенными ID (по умолчанию они ``1`` и ``5``): ``--start_id`` и ``--end_id``.

Обложки сохраняются в папку  ``images/``, тексты книг в папку ``books/``.
Для изменения папки с указанными подпапками, запустите код с параметром ``--dest_folder``


## Пример использования

```
$ python3 main.py --start_id 12 --end_id 14
Название: Бизнес со скоростью мысли
Автор: Гейтс Билл
Название: Блеск и нищета информационных технологий. Почему ИТ не являются конкурентным преимуществом
Автор: Карр Николас Дж.
```

## Скачивание книг категории "Фантастика" и создание каталога в формате JSON

Код скачивает книги в указанной категории начиная со страницы сайта ``--start_page``, и заканчивая ``--end_page``. По умолчанию ``1`` и ``5`` соответственно.

Запуск скрипта производится командой (для примера страницы ``5`` и ``10``)

```
python3 parsing_tululu_category.py --start_page 5 --end_page 10
```
Для изменения параметров, запустите код с со следующими аргументами: 

``--dest_folder`` Путь к каталогу с результатами парсинга: картинкам, книгам, JSON (по умолчанию ``catalog/``)

```
python3 parsing_tululu_category.py --dest_folder new_catalog/
```

``--skip_imgs`` Не скачивать картинки

```
python3 parsing_tululu_category.py --skip_imgs
```

``--skip_txt`` Не скачивать книги

```
python3 parsing_tululu_category.py --skip_txt
```

``--json_path`` Указать свой путь к *.json файлу с результатами

```
python3 parsing_tululu_category.py --json_path new_json_path_folder/
```
## Создание библиотеки скачанных книг из книг категории фантастика

Запустите скачивание книг по категории как указано в пункет выше и дождитесь создания каталога в формате ``JSON``

После чего запустите код командой:

```
python3 server.py 
```

Откройте файл ``index.html``

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков http://dvmn.org.

## Лицензия

Код распространяется свободно согласно MIT License
