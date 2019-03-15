# Mini readability app

Приложение собирает полезную информацию cо страницы, отбрасывая мусор, и сохраняет в текстовый файл.

### Установка

- git clone
- install python 3.x
- pipenv install
- изменить settings.json

### Настройки - settings.json

Если файла настроек нет, он создаться при первом запуске программы, а программа выполниться с настройками по умолчанию.

Селекторы для выборки контента
```text
   "main_content_selector":"p",
```

Селекторы для разрешения выборки контента, во вложенных тегах основного селектора
```text
   "nested_selectors":[  
      "p",
      "i",
      "span",
      "a"
   ],
```

Селектор  заголовка
```text
   "title_selector":"h1",
```

Ограничение количества символов в строке
```text
   "max_row_length":80,
```

Селектор для исключения тегов
```text
   "exclude_selectors":[  
      "header",
      "footer"
   ],
```

Сохранение ссылок в тексте (1 - сохранять, 0 - не сохранять)
```text
   "do_save_urls": 1
```

Настройки по умолчанию:
```json
{
   "main_content_selectors":"p",
   "nested_selectors":[
      "p",
      "i",
      "span",
      "a",
      "b",
      "strong"
   ],
   "title_selector":"h1",
   "max_row_length":80,
   "exclude_selectors":[
      "header",
      "footer"
   ],
   "do_save_urls": 0
}
```

## Запуск 

python main.py url

## Алгоритм работы

В настройках указываются селекторы для фильтрации тегов. По умолчанию селектор основного контента установлен тег параграфа "\<p\>"
Для парсинга страницы мы создали класс MyHTMLParser который наследуется от класса HTMLParser. В нём переопределенны методы обработки тегов (открытие, закрытие тегов, получение текста внутри тега).
С помощью библиотеки Requests мы получаем необработанное тело запрашиваемой страницы и передаем в экземпляр класса MyHTMLParser, который отбрасывает "мусор". Полученный текст форматируется и записывается в файл. 

## Результаты парсинга

https://www.gazeta.ru/politics/2019/03/14_a_12241927.shtml - Текст страницы без мусора

https://lenta.ru/news/2019/03/15/more/ - Текст страницы без мусора

https://news.yandex.ru/story/V_Ufe_postroyat_sportkompleks_stoimostyu_v_13_mlrd_rublej--756bf9ccd9dc107b84ee4937f87c6795 - Текст страницы не получен из-за отсутствия тегов параграфа \<p\>

https://proufu.ru/news/economika/77645-protezhe_byvshego_glavy_minzdrava_bashkirii_popalas_na_insuline/ - Текст получен с небольшим количеством мусора, текст читабелен.

https://gorobzor.ru/novosti/ekonomika/24362-otzyv-licenzii-roskomsnabbanka-mozhet-otrazitsya-na-vyvoze-musora-v-bashkirii - Текст получен с небольшим количеством мусора, текст читабелен.

https://sport.pravda.ru/news/1409954-biathlon/ - Текст страницы без мусора

## Итог

Учитывая не идеальный результат на всех страницах, в дальнейшем нужно добавить:
 - Более тонкую настройку фильтров. 
 - Привязку фильтров к домену.
 - Парсинг страниц из файла.