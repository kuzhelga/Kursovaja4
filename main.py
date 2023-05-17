from classes import HeadHunter, SuperJob, JsonSaver

# кол-во страниц для загрузки (на каждой по 100 вакансий)
PAGES_NUMBER = 1


def main():
    vacancies_json = []
    keyword = input("Введите слово для поиска вакансии: ")

    superjob = SuperJob(keyword)
    headhunter = HeadHunter(keyword)

    for api in (superjob, headhunter):
        api.get_vacancies(pages=PAGES_NUMBER)
        vacancies_json.extend(api.get_formatted_vacancies())

    jsonsaver = JsonSaver(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input(
            "1 - Вывести список вакансий\n"
            "2 - Отсортировать список по минимальной зп\n"
            "3 - Отсортировать список по максимальной зп\n"
            "4 - Очистить список вакансий и выйти\n"
            "q - Выход \n"
        )
        if command.lower() == 'q':
            break
        elif command == '1':
            vacancies = jsonsaver.vacancies_list()
        elif command == '2':
            vacancies = jsonsaver.sorted_vacancies_by_min_salary()
        elif command == '3':
            vacancies = jsonsaver.sorted_vacancies_by_max_salary()
        elif command == '4':
            vacancies = jsonsaver.delete_vacancies()
            break
        else:
            print('Введено некорректное значение')
            break

        for vacancy in vacancies:
            print(vacancy, end='\n\n')


if __name__ == "__main__":
    main()
