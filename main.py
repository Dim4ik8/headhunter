import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

HH_URL = 'https://api.hh.ru/vacancies/'
SUPERJOB_URL = 'https://api.superjob.ru/2.0/vacancies/'
LANGUAGES = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']
TABLE_DATA_HEADERS = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

def predict_rub_salary(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == "RUR":
        if vacancy['salary']['from'] and vacancy['salary']['to']:
            return (int(vacancy['salary']['from']) + int(vacancy['salary']['to'])) / 2
        if vacancy['salary']['from'] and (vacancy['salary']['to'] == None):
            return int(vacancy['salary']['from']) * 1.2
        if (vacancy['salary']['from'] == None) and vacancy['salary']['to']:
            return int(vacancy['salary']['to']) * 0.8
    else:
        return None


def predict_rub_salary_for_superJob(vacancy):
    if (vacancy['payment_from'] or vacancy['payment_to']) and vacancy['currency'] == "rub":
        if vacancy['payment_from'] and vacancy['payment_to']:
            return (int(vacancy['payment_from']) + int(vacancy['payment_to'])) / 2
        if vacancy['payment_from']:
            return int(vacancy['payment_from']) * 1.2
        if vacancy['payment_to']:
            return int(vacancy['payment_to']) * 0.8
    else:
        return None


def get_developer_salary_for_hh(language):
    vacancies_on_hh = []

    for page in count(0):

        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1', 'page': {page}}
        page_response = requests.get(HH_URL, params=params)
        page_response.raise_for_status()

        vacancies = page_response.json()

        if vacancies['items']:
            vacancies_on_hh.append(vacancies)

        else:
            break

    statistics_for_salary = {}
    vacancies_processed = 0
    sum_of_salaries = 0
    for page in vacancies_on_hh:

        for vacancy in page['items']:
            salary = predict_rub_salary(vacancy)
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        print('Wrong data from server.. Try one more time')

    statistics_for_salary = {
        language: {'vacancies_found': vacancies_on_hh[0]['found'],
                    'vacancies_processed': vacancies_processed,
                    'average_salary': average_salary
                    }
    }

    return statistics_for_salary


def get_developer_salary_for_superJob(language, token):
    vacancies_on_superjob = []

    for page in count(0):

        params = {'keyword': f'программист {language}', 'page': {page}}
        headers = {'X-Api-App-Id': token}
        response = requests.get(SUPERJOB_URL, params=params, headers=headers)
        response.raise_for_status()

        vacancies = response.json()

        if vacancies['objects']:
            vacancies_on_superjob.append(vacancies)

        else:
            break

    statistics_for_salary = {}
    vacancies_processed = 0
    sum_of_salaries = 0
    for page in vacancies_on_superjob:

        for vacancy in page['objects']:
            salary = predict_rub_salary_for_superJob(vacancy)
            if salary:
                vacancies_processed += 1
                sum_of_salaries += salary
    try:
        average_salary = round((sum_of_salaries) / vacancies_processed)
    except ZeroDivisionError:
        print('Wrong data from server.. Try one more time')
    statistics_for_salary = {
        language: {'vacancies_found': vacancies_on_superjob[0]['total'],
                   'vacancies_processed': vacancies_processed,
                   'average_salary': average_salary
                   }
    }

    return statistics_for_salary


def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_KEY')
    try:

        for language in LANGUAGES:
            vacancies_in_table = []
            for key, value in get_developer_salary_for_superJob(language, token).items():
                vacancies_in_table.extend([key, value['vacancies_found'], value['vacancies_processed'], value['average_salary']])

            TABLE_DATA_HEADERS.append(vacancies_in_table)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    table = AsciiTable(TABLE_DATA_HEADERS, title='SuperJobMoscow')
    print(table.table)

    try:

        for language in LANGUAGES:
            vacancies_in_table = []
            for language, vacancies in get_developer_salary_for_hh(language).items():
                vacancies_in_table.extend([language, vacancies['vacancies_found'], vacancies['vacancies_processed'], vacancies['average_salary']])

            TABLE_DATA_HEADERS.append(vacancies_in_table)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))


    table = AsciiTable(TABLE_DATA_HEADERS, title='HeadhunterMoscow')
    print(table.table)

if __name__ == '__main__':
    main()
