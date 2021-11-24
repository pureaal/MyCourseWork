import re
import hashlib
from multiprocessing.dummy import Pool

import requests
from bs4 import BeautifulSoup as BS


class CheckFromUrl:
    @staticmethod
    def makeRequest(hash_md5):
        try:
            req = requests.get(f'https://md5.gromweb.com/?md5={hash_md5}')
            return req.content
        except:
            return "Сайт не отвечает!"

    @staticmethod
    def parseRequest(html):
        try:
            BSobj = BS(html, 'html.parser')
            encodedHash = BSobj.find('em', {'class': 'long-content string'})
            return encodedHash.text if encodedHash else None
        except:
            return 'Не удалось спарсить результат!'
    @staticmethod
    def CrackMd5HashOnline(hash_md5):
        try:
            html = CheckFromUrl.makeRequest(hash_md5)
            encodeHash = CheckFromUrl.parseRequest(html)
            return encodeHash
        except:
            return 'Не удалось провести проверку через сайт :('


class CheckFromFile:
    @staticmethod
    def md5(password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    @classmethod
    def check_pass(cls, argv):
        password, hash_ = argv

        if hash_ == cls.md5(password):
            return password
        else:
            return None


    @classmethod
    def CrackMd5HashByDict(cls, path_dict, hash_):
        try:
            passwords = open(path_dict, 'r').readlines()
        except Exception:
            print(f"Файл {path_dict} не найден! ")
            path_dict = input('Введите путь до словаря с паролями: ')
            passwords = open(path_dict, 'r').readlines()
        passwords = map(lambda s: s.strip(), passwords)
        data = ((password, hash_) for password in passwords)
        pool = Pool(5)
        result = pool.map(cls.check_pass, data)
        for password in result:
            print(password)
            if password:
                return password
        return None


    
if __name__ == '__main__':
    DICT_PATH = r'passwords.txt'
    hash_ = input('Введите MD5 hash: ').lower()
    if not re.match(r'^[\w]{32}$', hash_):
        print('Вы ввели некорректный MD5 хэш')
        exit()

    sitePasswordCheck = CheckFromUrl.CrackMd5HashOnline(hash_)
    #if sitePasswordCheck is None:
    if not sitePasswordCheck:
        print(f'Введённый Вами хэш -- {hash_} -- отсутствует в базе данных сайта. ')
        print(f'Подбираем пароль по словарю....')
        password = CheckFromFile.CrackMd5HashByDict(DICT_PATH, hash_)
        if password:
            print(f'Пароль найден.\nДля хэша: {hash_} подходит пароль: {password}')
        else:
            print(f'Пароль не найден :(')
    else:
        print(f'Проверка через сайт. Для хэша: {hash_} подходит пароль: {sitePasswordCheck}')
