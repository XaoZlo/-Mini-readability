import os
import sys
import argparse
import requests
import urllib.parse
import json
from html.parser import HTMLParser


class Main:

    def __init__(self):

        self.cur_dir = os.getcwd()
        self.url = self.get_url_from_argv()
        self.raw_html = self.get_raw_html()
        self.settings = {
            'main_content_selectors': 'p',
            'nested_selectors': ['p', 'i', 'span', 'a'],
            'title_selector': 'h1',
            'max_row_length': 80,
            'exclude_selectors': ['header', 'footer'],
            'do_save_urls': 1
        }
        self.get_settings()
        parser = MyHTMLParser(self.url, self.settings)
        parser.feed(self.raw_html)
        self.content = self.make_rows(parser.content)

    def get_settings(self):
        f = self.cur_dir + '/settings.json'
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as f:
                try:
                    dump_settings = json.loads(f.read())
                    for key in self.settings.keys():
                        if key not in dump_settings:
                            print('Не хватает опций в настройках.\nИспользуем настройки по умолчаниюю.\n')
                            return
                    self.settings = dump_settings
                except json.decoder.JSONDecodeError:
                    print('Не удалось загрузить настройки.\nИспользуем настройки по умолчаниюю.\n')
        else:
            with open(f, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f)

    def get_raw_html(self):
        """Юзер агент чтобы сайты не думали что мы робот"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0'
        }

        try:
            response = requests.get(self.url, headers=headers)
            if response.status_code is not 200:
                print("Что-то пошло не так...")
                sys.exit()
            return response.text
        except requests.exceptions.InvalidSchema:
            print('Неправильная ссылка')

    def get_argv(self):
        parser = self.create_argv_parser()
        args = parser.parse_args(sys.argv[1:])
        return args

    def create_argv_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('url', type=str)

        return parser

    def get_url_from_argv(self):
        url = self.get_argv().url
        return url

    def write_to_file(self):

        """Вытаскиваем из ссылки строку после https://"""
        raw_url = urllib.parse.urlparse(self.url)

        raw_path = '%s%s' % (raw_url[1], raw_url[2])

        """Проверяем есть ли название файла"""
        file_batch = os.path.split(raw_path)
        if len(file_batch[1]) == 0:
            raw_path = '%s%s' % (file_batch[0], '.txt')
        else:
            raw_path = '%s%s%s' % (file_batch[0], file_batch[1].split('.')[0], '.txt')
        '''Меняем '/' на '\' '''
        raw_path = raw_path.replace('/', '\\')
        file_path = self.cur_dir + '\\' + raw_path
        dir_name = os.path.dirname(file_path)
        """Проверяем есть ли указанная директория"""
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(self.content)

    def make_rows(self, content):
        raw_text = content
        text = ''
        rows = []
        while raw_text:
            if len(raw_text) <= self.settings['max_row_length']:
                rows.append(raw_text)
                raw_text = ""
            else:
                line_break_pos = raw_text.find('\n\n')
                if line_break_pos < self.settings['max_row_length'] and line_break_pos != -1:
                    rows.append(raw_text[:line_break_pos] + '\n')
                    raw_text = raw_text[line_break_pos + 2:]
                    line_break_pos = 0
                else:
                    for i in range(self.settings['max_row_length'] + 1, 0, -1):
                        if str.isspace(raw_text[i]):
                            rows.append(raw_text[:i])
                            raw_text = raw_text[i + 1:]
                            break
                        if i == 1:
                            for k in range(0 , len(raw_text), + 1):
                                if str.isspace(raw_text[k]):
                                    rows.append(raw_text[:k])
                                    raw_text = raw_text[k + 1:]
                                    break

        for s in rows:
            text = '%s%s\n' % (text, s)

        return text


class MyHTMLParser(HTMLParser):

    def __init__(self, url, settings):
        super().__init__()
        self.user = 'x'

        self.content = ''
        self.recording = 0
        self.exclude_flag = 0
        self.paragraph_flag = 0
        self.url_flag = 0
        self.url_to_write = ''
        self.title_flag = 0
        self.nested_flag = 0
        self.hostname = urllib.parse.urlparse(url)[1]
        self.settings = settings

    def handle_starttag(self, tag, attrs):
        if tag in self.settings['exclude_selectors']:
            self.exclude_flag = 1
            return

        if tag in self.settings['nested_selectors']:
            self.nested_flag = 1
        else:
            self.nested_flag = 0

        if tag == 'a' and self.recording and self.nested_flag and self.settings['do_save_urls'] == 1:
            self.url_flag = 1
            self.url_to_write = attrs[0][1]
            if not urllib.parse.urlparse(self.url_to_write)[1]:
                self.url_to_write = '%s%s' % (self.hostname, self.url_to_write)

        if tag in self.settings['title_selector']:
            self.title_flag = 1

        if tag in self.settings['main_content_selectors']:
            self.recording = 1
        else:
            return

    def handle_endtag(self, tag):
        if tag in self.settings['exclude_selectors'] and self.exclude_flag:
            self.exclude_flag = 0
            return

        if tag in self.settings['nested_selectors'] and self.nested_flag:
            self.nested_flag = 0
            return

        if tag == self.settings['main_content_selectors'] and self.recording:
            self.recording -= 1
            self.paragraph_flag = 1

    def handle_data(self, data):
        if self.exclude_flag:
            return

        if self.title_flag:
            self.content = '%s%s%s' % (self.content, data, '\n\n')
            self.title_flag = 0

        if self.recording:
            if self.paragraph_flag:
                self.content = '%s%s%s' % (self.content, '\n\n', data)
                self.paragraph_flag = 0

            if self.nested_flag:
                self.content = '%s%s' % (self.content, data)
                self.nested_flag = 0
            else:
                self.content = '%s%s' % (self.content, data)

            if self.url_flag:
                self.content = '%s [%s]' % (self.content, self.url_to_write)
                self.url_flag = 0


if __name__ == '__main__':
    main = Main()
    main.write_to_file()
