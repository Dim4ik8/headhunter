import requests
from pprint import pprint
from itertools import count

url = 'https://api.hh.ru/vacancies/'
languages = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']

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

def get_developer_salary_info(language):
    list_of_vacancies = []

    for page in count(0):

        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1', 'page': {page}}
        page_response = requests.get(url, params=params)
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

    average_salary = round((sum_of_salaries)/vacancies_processed)

    statistics_for_salary[language] = {'vacancies_found': list_of_vacancies[0]['found']}
    statistics_for_salary[language].update({'vacancies_processed': vacancies_processed })
    statistics_for_salary[language].update({'average_salary': average_salary })

    return statistics_for_salary

def main():
    try:
        for language in languages:
            print(get_developer_salary_info(language))
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))






if __name__ == '__main__':
    main()
