import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

HH_URL = 'https://api.hh.ru/vacancies/'
SUPERJOB_URL = 'https://api.superjob.ru/2.0/vacancies/'
LANGUAGES = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']
HEADERS_FOR_VACANCIES_TABLE = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']


def predict_rub_salary_from_site(vacancy, site):
    if site == 'hh':
        if not vacancy['salary'] or not vacancy['salary']['currency'] == "RUR":
            return None
        else:
            if vacancy['salary']['from'] and vacancy['salary']['to']:
                return (int(vacancy['salary']['from']) + int(vacancy['salary']['to'])) / 2
            elif vacancy['salary']['from'] and not vacancy['salary']['to']:
                return int(vacancy['salary']['from']) * 1.2
            elif not vacancy['salary']['from'] and vacancy['salary']['to']:
                return int(vacancy['salary']['to']) * 0.8
    elif site == 'superjob':

        if (vacancy['payment_from'] or vacancy['payment_to']) and vacancy['currency'] == "rub":
            if vacancy['payment_from'] and vacancy['payment_to']:
                return (int(vacancy['payment_from']) + int(vacancy['payment_to'])) / 2
            if vacancy['payment_from']:
                return int(vacancy['payment_from']) * 1.2
            if vacancy['payment_to']:
                return int(vacancy['payment_to']) * 0.8
        else:
            return None


def get_statistics_for_salary_on_hh(language):
    hh_vacancies = []

    for page in count(0):

        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1', 'page': {page}}
        page_response = requests.get(HH_URL, params=params)
        page_response.raise_for_status()

        vacancies = page_response.json()

        if vacancies['items']:
            hh_vacancies.append(vacancies)

        else:
            break

    vacancies_processed = 0
    sum_of_salaries = 0
    for page in hh_vacancies:

        for vacancy in page['items']:
            salary = predict_rub_salary_from_site(vacancy, 'hh')
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        print('Wrong data from server.. Try one more time')

    statistics_for_salary = {
        language: {'vacancies_found': hh_vacancies[0]['found'],
                   'vacancies_processed': vacancies_processed,
                   'average_salary': average_salary
                   }
    }

    return statistics_for_salary


def get_statistics_for_salary_on_superJob(language, token):
    superjob_vacancies = []

    for page in count(0):

        params = {'keyword': f'программист {language}', 'page': {page}}
        headers = {'X-Api-App-Id': token}
        response = requests.get(SUPERJOB_URL, params=params, headers=headers)
        response.raise_for_status()

        vacancies = response.json()

        if vacancies['objects']:
            superjob_vacancies.append(vacancies)

        else:
            break

    vacancies_processed = 0
    sum_of_salaries = 0
    for page in superjob_vacancies:

        for vacancy in page['objects']:
            salary = predict_rub_salary_from_site(vacancy, 'superjob')
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        print('Wrong data from server.. Try one more time')
    statistics_for_salary = {
        language: {'vacancies_found': superjob_vacancies[0]['total'],
                   'vacancies_processed': vacancies_processed,
                   'average_salary': average_salary
                   }
    }

    return statistics_for_salary


def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_KEY')
    # Выводим в консоль вакансии с hh.ru только по Москве (первую страницу)
    params = {'text': 'программист', 'search_field': 'name', 'premium': True, 'area': '1', 'page': '1',
              'period': '30'}
    response = requests.get(HH_URL, params=params)
    response.raise_for_status()

    vacancies = response.json()
    print(f"Всего найдено {vacancies['found']} вакансий на headhunter.ru")
    if vacancies:
        for vacancy in vacancies['items']:
            print(vacancy['name'])

    # Выводим в консоль вакансии с superjob.ru только по Москве (первую страницу)
    params = {'keyword': 'Программист', 'page': '1', 'town': 'Москва', 'profession_only': '1'}
    headers = {'X-Api-App-Id': token}
    response = requests.get(SUPERJOB_URL, params=params, headers=headers)
    response.raise_for_status()

    vacancies = response.json()
    print(f"Всего найдено {vacancies['total']} вакансий на superjob.ru")
    if vacancies:

        for vacancy in vacancies['objects']:
            print(f"{vacancy['profession']}, {vacancy['town']['title']}")

    superjob_vacancies = []

    try:
        superjob_vacancies.append(HEADERS_FOR_VACANCIES_TABLE)
        for language in LANGUAGES:
            statistics = []
            for language, vacancies in get_statistics_for_salary_on_superJob(language, token).items():
                statistics.extend([language, vacancies['vacancies_found'], vacancies['vacancies_processed'],
                                           vacancies['average_salary']])

            superjob_vacancies.append(statistics)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:{0}".format(error))

    table = AsciiTable(superjob_vacancies, title='SuperJobMoscow')
    print(table.table)

    hh_vacancies= []
    try:

        hh_vacancies.append(HEADERS_FOR_VACANCIES_TABLE)
        for language in LANGUAGES:
            statistics = []
            for language, vacancies in get_statistics_for_salary_on_hh(language).items():
                statistics.extend([language, vacancies['vacancies_found'], vacancies['vacancies_processed'],
                                           vacancies['average_salary']])

            hh_vacancies.append(statistics)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    table = AsciiTable(hh_vacancies, title='HeadhunterMoscow')
    print(table.table)


if __name__ == '__main__':
    main()
