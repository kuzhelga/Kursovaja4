import json
import os
from abc import ABC, abstractmethod
from pprint import pprint

import requests as requests

PAGES_NUMBER = 2


class Simple(ABC):
    """Абстрактный класс для наследования классов с API"""

    @abstractmethod
    def get_requests(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class File(ABC):
    """Абстрактный класс для наследования JsonSaver"""

    @abstractmethod
    def add_vacancies(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def delete_vacancies(self):
        pass

class SuperJob(Simple):

    def __init__(self, keyword):
        """Класс для получения списка вакансий с сайта SuperJob"""
        self.__url = "https://api.superjob.ru/2.0/vacancies/"
        self.__headers = {"X-Api-App-Id": os.getenv("API_SuperJob")}
        self.__params = {"keyword": keyword, "page": 0, "count": 100}
        self.__vacancies = []

    @staticmethod
    def get_salary(salary, currency):
        """Статический метод возвращает зарплату в рублях, если она указана в валюте"""
        formatted_salary = None
        if salary and salary != 0:
            formatted_salary = salary if currency == 'rub' else salary * 80
        return formatted_salary

    def get_requests(self):
        response = requests.get(self.__url, headers=self.__headers, params=self.__params)
        # передаем ключ API, ключевое слово для поиска и кол-во результатов на страницу
        if response.status_code != 200:
            print(f"Ошибка получения данных по API! code {response.status_code}")
        else:
            print("Информация загружена")
        return response.json()['objects']

    def get_vacancies(self, pages=3):
        while self.__params['page'] < pages:
            print(f"SuperJob, поиск данных на странице {self.__params['page'] + 1}", end=": ")
            try:
                values = self.get_requests()
            except requests.exceptions.RequestException as e:
                print("Ошибка!")
                break
            print(f"Всего вакансий: {len(values)}")
            self.__vacancies.extend(values)
            self.__params['page'] += 1

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
                formatted_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['profession'],
                'url': vacancy['link'],
                'salary_from': self.get_salary(vacancy['payment_from'], vacancy['currency']),
                'salary_to': self.get_salary(vacancy['payment_to'], vacancy['currency']),
                'employer': vacancy['firm_name'],
                'api': 'SuperJob'
            })
        return formatted_vacancies

class HeadHunter(Simple):
    """Класс для получения списка вакансий с сайта HeadHunter"""
    def __init__(self, keyword):
        self.__url = "https://api.hh.ru/vacancies"
        self.__headers = {"User-Agent": "Google Chrome"}
        self.__params = {"keyword": keyword, "page": 0, "per_page": 100}
        self.__vacancies = []

    @staticmethod
    def get_salary(salary):
        """Статический метод возвращает зарплату в рублях, если она указана в валюте"""
        formatted_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formatted_salary[0] = salary['from'] if salary['currency'].lower() == 'rub' else salary['from'] * 80
        if salary and salary['to'] and salary['to'] != 0:
            formatted_salary[1] = salary['to'] if salary['currency'].lower() == 'rub' else salary['to'] * 80
        return formatted_salary

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
            self.__vacancies.extend(values)
            self.__params['page'] += 1

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            formatted_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['name'],
                'url': vacancy['alternate_url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer': vacancy['employer']['name'],
                'api': 'HeadHunter'
            })
        return formatted_vacancies

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

    def __gt__(self, other):
        if not other.salary_from:
            return True
        elif not self.salary_from:
            return False
        return self.salary_from >= other.salary_from


class JsonSaver(File):
    """Класс для сохранения вакансий в файл в формате в json и работы со списком вакансий из файла"""
    def __init__(self, keyword, vacancies_json):
        self.__filename = f"{keyword.title()}.json"

    def create_json(self, vacancies_json):
        """Метод записи данных в файл json"""
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def vacancies_list(self):
        """Метод записи вакансий в файл json с определенными полями"""
        with open(self.__filename, 'w', encoding='utf-8') as file:
            data = json.load(file)
            vacancies = [Vacancies(x['id'], x['title'], x['url'], x['salary_from'], x['salary_to'], x['employer'], x['api']) for x in data]
        return vacancies
