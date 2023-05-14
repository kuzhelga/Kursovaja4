import os
from abc import ABC, abstractmethod
from pprint import pprint

import requests as requests


class Simple(ABC):
    """Абстрактный класс для наследования"""

    @abstractmethod
    def get_requests(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class SuperJob(Simple):

    def __init__(self, keyword):
        """Класс для получения списка вакансий с сайта SuperJob"""
        self.__url = "https://api.superjob.ru/2.0/vacancies/"
        self.__headers = {"X-Api-App-Id": os.getenv("API_SuperJob")}
        self.__params = {"keyword": keyword, "page": 0, "count": 100}
        self.__vacancies = []

    def get_requests(self):
        response = requests.get(self.__url, headers=self.__headers, params=self.__params)
        # передаем ключ API, ключевое слово для поиска и кол-во результатов на страницу
        if response.status_code != 200:
            print(f"Ошибка получения данных по API! code {response.status_code}")
        else:
            print("Информация загружена")
        return response.json()['objects']

    def get_vacancies(self, pages=1):
        while self.__params['page'] < pages:
            print(f"SuperJob, поиск данных на странице {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_requests()
            except requests.exceptions.RequestException as e:
                print("Ошибка!")
                break
            print(f"Всего вакансий: {len(values)}")
            self.__vacancies.append(values)
            self.__params['page'] += 1


class HeadHunter(Simple):
    """Класс для получения списка вакансий с сайта HeadHunter"""
    def __init__(self, keyword):
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "Google Chrome"}
        self.__params = {"keyword": keyword, "page": 0, "per_page": 100}
        self.__vacancies = []

    def get_requests(self):
        response = requests.get(self.__url, headers=self.__headers, params=self.__params)
        # передаем ключевое слово для поиска и кол-во результатов на страницу
        if response.status_code != 200:
            print(f"Ошибка получения данных по API! code {response.status_code}")
        else:
            print("Информация загружена")
        return response.json()['items']

    def get_vacancies(self, pages=2):
        while self.__params['page'] < pages:
            print(f"HeadHunter, поиск данных на странице {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_requests()
            except requests.exceptions.RequestException as e:
                print("Ошибка!")
                break
            print(f'Всего вакансий: {len(values)}')
            self.__vacancies.append(values)
            self.__params['page'] += 1


class Vacancies:
    """Класс для отображения вакансий с ограниченными полями"""
    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer, api):
        self.vacancy_id = vacancy_id
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.employer = employer
        self.api = api

    def __str__(self):
        salary_from = f'от {self.salary_from}' if self.salary_from is not None else ''
        salary_to = f'до {self.salary_to}' if self.salary_to is not None else ''
        if self.salary_from is None and self.salary_to is None:
            self.salary_from = 0
        return f'''Вакансия \"{self.title}\" \nКомпания: \"{self.employer}\" \nЗарплата: {salary_from} {salary_to}\n
        URL: {self.url}'''

class JsonSaver:
    """Класс для сохранения вакансий в файл в удобном формате в json"""
    def __init__(self, keyword):
        pass


sj = HeadHunter("python")
pprint(sj.get_requests())
pprint(sj.get_vacancies())
