import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os
import logging

HH_URL = 'https://api.hh.ru/vacancies/'
SUPERJOB_URL = 'https://api.superjob.ru/2.0/vacancies/'
LANGUAGES = [
    'Javascript',
    'Java',
    'Python',
    'Ruby',
    'PHP',
    'C#',
    'C',
    'Go',
    'Swift',
    'Scala'
]
HEADERS_FOR_VACANCIES_TABLE = [
    'Язык программирования',
    'Вакансий найдено',
    'Вакансий обработано',
    'Средняя зарплата'
]


def get_avg_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        average_salary = int(salary_from) * 1.2

    elif not salary_from and salary_to:
        average_salary = int(salary_to) * 0.8

    else:
        average_salary = (int(salary_from) + int(salary_to)) / 2

    return average_salary


def predict_rub_salary_from_hh(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == "RUR":
        average_salary = get_avg_salary(vacancy['salary']['from'], vacancy['salary']['to'])
        return average_salary


def predict_rub_salary_from_superjob(vacancy):
    if (vacancy['payment_from'] or vacancy['payment_to']) and vacancy['currency'] == "rub":
        average_salary = get_avg_salary(vacancy['payment_from'], vacancy['payment_to'])
        return average_salary


def get_salary_statistics_on_hh(language):
    hh_vacancies = []
    moscow = '1'
    for page in count(0):

        params = {
            'text': f'программист {language}',
            'search_field': 'name',
            'premium': True,
            'area': moscow,
            'page': {page}
        }
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
            salary = predict_rub_salary_from_hh(vacancy)
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        logging.error('Wrong data from server.. Try one more time')

    salary_statistics = {
        language: {
            'vacancies_found': hh_vacancies[0]['found'],
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    }

    return salary_statistics


def get_salary_statistics_on_superJob(language, token):
    superjob_vacancies = []

    for page in count(0):

        params = {
            'keyword': f'программист {language}',
            'page': {page},
            'town': 'Москва'
        }
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
            salary = predict_rub_salary_from_superjob(vacancy)
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        logging.error('Wrong data from server.. Try one more time')
    salary_statistics = {
        language: {
            'vacancies_found': superjob_vacancies[0]['total'],
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }
    }

    return salary_statistics


def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_KEY')

    superjob_table_strings = []
    try:
        superjob_table_strings.append(HEADERS_FOR_VACANCIES_TABLE)
        for language in LANGUAGES:
            statistics = []
            for language, vacancies in get_salary_statistics_on_superJob(language, token).items():
                statistics.extend(
                    [language, vacancies['vacancies_found'],
                    vacancies['vacancies_processed'],
                    vacancies['average_salary']]
                )

            superjob_table_strings.append(statistics)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:{0}".format(error))

    table = AsciiTable(superjob_table_strings, title='SuperJobMoscow')
    print(table.table)

    hh_table_strings = []
    try:
        hh_table_strings.append(HEADERS_FOR_VACANCIES_TABLE)
        for language in LANGUAGES:
            statistics = []
            for language, vacancies in get_salary_statistics_on_hh(language).items():
                statistics.extend(
                    [language, vacancies['vacancies_found'],
                    vacancies['vacancies_processed'],
                    vacancies['average_salary']]
                )

            hh_table_strings.append(statistics)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    table = AsciiTable(hh_table_strings, title='HeadhunterMoscow')
    print(table.table)


if __name__ == '__main__':
    main()
