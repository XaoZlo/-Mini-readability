import os
import re
import sys
import argparse
import requests
from html.parser import HTMLParser


class Main:

    def __init__(self):

        self.cur_dir = os.getcwd()
        self.url = self.get_url_from_argv()
        self.raw_html = self.get_raw_html()
        parser = MyHTMLParser()
        parser.feed(self.raw_html)
        self.content = parser.article
        print(parser.article)
        pass

    def get_settings(self):
        settings_file = self.cur_dir + '/setings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as settings:
                print(settings.readline())
        else:
            print('Нет файла настроек!')

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
        parsed_path = re.search(r'^(.*:)//(.*)/$', self.url)
        '''Меняем '/' на '\' '''
        parsed_path = parsed_path.replace('/', '\\')

        file_name =  self.cur_dir + '\\' + parsed_path + '.txt'
        dir_name = os.path.dirname(file_name)
        """Проверяем есть ли указанная директория"""
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(file_name, 'w', encoding="utf-8") as file:
            file.write(self.content)

        return True


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.user = 'x'

        self.article = ''
        self.recording = 0
        self.exclude_flag = 0
        self.selectors = {
            'main_content_selector': 'p',
            'nested_selectors': ['p', 'i', 'span', 'a'],
            'title': 'h1',
            'article': 'article',
        }
        self.exclude_selectors = ['header', 'footer']
        pass

    def handle_starttag(self, tag, attrs):
        if tag in self.exclude_selectors:
            self.exclude_flag = 1
            return
        if tag in self.selectors['main_content_selector']:
            pass
        else:
            return
        #if self.recording:
         #  self.recording += 1
         #   return
        self.recording = 1

    def handle_endtag(self, tag):
        if tag in self.exclude_selectors and self.exclude_flag:
            self.exclude_flag = 0
            return
        if tag == self.selectors['main_content_selector'] and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.exclude_flag == 1:
            return
        if self.recording:
            self.article = self.article + data + '\n\n'
            self.recording = False


if __name__ == '__main__':
    main = Main()

    main.write_to_file()
