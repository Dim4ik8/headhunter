import requests
from pprint import pprint

def predict_rub_salary(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == "RUR":
        if vacancy['salary']['from'] and vacancy['salary']['to']:
            return (int(vacancy['salary']['from']) + int(vacancy['salary']['to']))/2
        if vacancy['salary']['from'] and (vacancy['salary']['to'] == None):
            return int(vacancy['salary']['from'])*1.2
        if (vacancy['salary']['from'] == None) and vacancy['salary']['to']:
            return int(vacancy['salary']['to'])*0.8
    else:
        return None



def main():
    url = 'https://api.hh.ru/vacancies/'
    languages = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']

    statistics = {}
    for language in languages:
        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1'}

        response = requests.get(url, params=params)
        response.raise_for_status()

        vacancies = response.json()
        if int(vacancies['found']) > 100:
            statistics[language] = vacancies['found']

    pprint(statistics)

    params = {'text': 'программист Python', 'search_field': 'name', 'premium': True,
              'area': '1'}
    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancies = response.json()

    for vacancy in vacancies['items']:
        print(predict_rub_salary(vacancy))



if __name__ == '__main__':
    main()
