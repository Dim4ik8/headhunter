import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

HH_URL = 'https://api.hh.ru/vacancies/'
SUPERJOB_URL = 'https://api.superjob.ru/2.0/vacancies/'
LANGUAGES = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']


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


def get_developer_salary_info(language):
    list_of_vacancies = []

    for page in count(0):

        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1', 'page': {page}}
        page_response = requests.get(HH_URL, params=params)
        page_response.raise_for_status()

        vacancies = page_response.json()

        if vacancies['items']:
            list_of_vacancies.append(vacancies)

        else:
            break

    statistics_for_salary = {}
    vacancies_processed = 0
    sum_of_salaries = 0
    for page in list_of_vacancies:

        for vacancy in page['items']:

            if predict_rub_salary(vacancy):
                vacancies_processed += 1
                sum_of_salaries += predict_rub_salary(vacancy)

    average_salary = round((sum_of_salaries) / vacancies_processed)

    statistics_for_salary[language] = {'vacancies_found': list_of_vacancies[0]['found']}
    statistics_for_salary[language].update({'vacancies_processed': vacancies_processed})
    statistics_for_salary[language].update({'average_salary': average_salary})

    return statistics_for_salary


def get_developer_salary_info_for_superJob(language):
    list_of_vacancies = []
    secret_key = os.getenv('SUPERJOB_KEY')
    for page in count(0):

        params = {'keyword': f'программист {language}', 'page': {page}}
        headers = {'X-Api-App-Id': secret_key}
        response = requests.get(SUPERJOB_URL, params=params, headers=headers)
        response.raise_for_status()

        vacancies = response.json()

        if vacancies['objects']:
            list_of_vacancies.append(vacancies)

        else:
            break

    statistics_for_salary = {}
    vacancies_processed = 0
    sum_of_salaries = 0
    for page in list_of_vacancies:

        for vacancy in page['objects']:

            if predict_rub_salary_for_superJob(vacancy):
                vacancies_processed += 1
                sum_of_salaries += predict_rub_salary_for_superJob(vacancy)

    average_salary = round((sum_of_salaries) / vacancies_processed)

    statistics_for_salary[language] = {'vacancies_found': list_of_vacancies[0]['total']}
    statistics_for_salary[language].update({'vacancies_processed': vacancies_processed})
    statistics_for_salary[language].update({'average_salary': average_salary})

    return statistics_for_salary


def main():
    load_dotenv()

    table_data_superjob = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    try:

        for language in LANGUAGES:
            a = []
            get_developer_salary_info_for_superJob(language)
            for key, value in get_developer_salary_info_for_superJob(language).items():
                a.extend([key, value['vacancies_found'], value['vacancies_processed'], value['average_salary']])

            table_data_superjob.append(a)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))

    table = AsciiTable(table_data_superjob, title='SuperJobMoscow')
    print(table.table)

    table_data_hh = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    try:

        for language in LANGUAGES:
            a = []
            get_developer_salary_info(language)
            for key, value in get_developer_salary_info(language).items():
                a.extend([key, value['vacancies_found'], value['vacancies_processed'], value['average_salary']])

            table_data_hh.append(a)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))


    table_hh = AsciiTable(table_data_hh, title='SuperJobMoscow')
    print(table_hh.table)

if __name__ == '__main__':
    main()
