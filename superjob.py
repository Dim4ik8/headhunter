import requests
import os
from itertools import count

from dotenv import load_dotenv

load_dotenv()
url = 'https://api.superjob.ru/2.0/vacancies/'
languages = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']

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

secret_key = os.getenv('SUPERJOB_KEY')


def get_developer_salary_info_for_superJob(language):
    list_of_vacancies = []

    for page in count(0):

        params = {'keyword': f'программист {language}', 'page': {page}}
        headers = {'X-Api-App-Id': secret_key}
        response = requests.get(url, params=params, headers=headers)
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

    average_salary = round((sum_of_salaries)/vacancies_processed)

    statistics_for_salary[language] = {'vacancies_found': list_of_vacancies[0]['total']}
    statistics_for_salary[language].update({'vacancies_processed': vacancies_processed })
    statistics_for_salary[language].update({'average_salary': average_salary })

    return statistics_for_salary


print(get_developer_salary_info_for_superJob('1C'))