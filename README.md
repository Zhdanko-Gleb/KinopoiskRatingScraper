# Kinopoisk Rating Scraper

## Описание
Kinopoisk Rating Scraper — это Python-скрипт для автоматического извлечения и сохранения персональных оценок фильмов с сайта Кинопоиск. Разработан из-за отсутствия официальной функции экспорта рейтингов на платформе Кинопоиск.

## Требования
- Python 3.6+
- Библиотеки:
  - requests
  - beautifulsoup4
  - pandas (для экспорта в CSV)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Zhdanko-Gleb/kinopoisk-rating-scraper.git
cd kinopoisk-rating-scraper
```

2. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

## Подготовка к использованию

### 1. Получение идентификатора пользователя (number_user)

Для работы скрипта необходимо получить ваш идентификатор пользователя:

1. Войдите в свой аккаунт на [Кинопоиске](https://www.kinopoisk.ru/)
2. Перейдите на страницу со своими оценками
3. Посмотрите на URL в адресной строке браузера, он должен иметь формат: `https://www.kinopoisk.ru/user/number_user/votes/`
4. Скопируйте число, которое находится на месте `number_user` в URL - это ваш идентификатор пользователя

### 2. Получение Cookie строки с Кинопоиска

Для полноценной работы скрипта также необходимо получить cookie-строку с вашей авторизованной сессии:

1. Войдите в свой аккаунт на Кинопоиске
2. Откройте страницу со своими оценками
3. Откройте инструменты разработчика (F12 или правой кнопкой мыши → Inspect)
4. Найдите Cookie:
   - В инструментах разработчика перейдите на вкладку "Network"
   - Обновите страницу (или перейдите на страницу с вашими оценками)
   - Найдите в списке запрос к `kinopoisk.ru` и кликните на него
   - Перейдите на вкладку "Headers"
   - Прокрутите вниз до раздела "Request Headers"
   - Найдите строку, начинающуюся с "Cookie:"
   - Скопируйте всю строку после `Cookie:`

### 3. Сохранение данных в файл cookies_file.py

После получения обоих параметров, создайте или отредактируйте файл `cookies_file.py` со следующим содержимым:

```python
# cookies_file.py
cookies_string = "ваша_cookie_строка_здесь"
number_user = "ваш_идентификатор_пользователя_здесь"
```

## Использование

После настройки необходимых параметров вы можете запустить скрипт:

```bash
python kinopoisk_scraper.py
```

## Структура проекта

- `kinopoisk_scraper.py` - основной скрипт для скрапинга
- `cookies_file.py` - файл для хранения cookie-строки и идентификатора пользователя
- `requirements.txt` - необходимые зависимости

## Важные примечания

- Скрипт разработан исключительно для личного использования
- Используйте скрипт с разумной частотой запросов, чтобы не создавать излишнюю нагрузку на сервера Кинопоиска
- Сайты могут менять свою структуру, что может привести к неработоспособности скрипта. В этом случае может потребоваться обновление кода.

## Ограничение ответственности

Данный инструмент предназначен только для личного использования. Автор не несет ответственности за любое неправомерное использование скрипта. Используйте на свой страх и риск.

## Лицензия

Этот проект распространяется под лицензией MIT. Смотрите файл [LICENSE](LICENSE) для получения дополнительной информации.

## Вклад в проект

Вклады приветствуются! Если у вас есть идеи или улучшения:

1. Форкните репозиторий
2. Создайте ветку для ваших изменений (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте изменения в ваш форк (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Автор
[Gleb Zhdanko](https://github.com/Zhdanko-Gleb)
