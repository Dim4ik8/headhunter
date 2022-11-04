import requests
from pprint import pprint


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


def main():
    url = 'https://api.hh.ru/vacancies/'
    languages = ['Javascript', 'Java', 'Python', 'Ruby', 'PHP', 'C#', 'C', 'Go', 'Swift', 'Scala']

    statistics_for_salary = {}

    for num, language in enumerate(languages):
        params = {'text': f'программист {language}', 'search_field': 'name', 'premium': True,
                  'area': '1'}

        response = requests.get(url, params=params)
        response.raise_for_status()

        vacancies = response.json()

        if vacancies['found'] > 100:
            statistics_for_salary[languages[num]] = {'vacancies_found': vacancies['found']}
            vacancies_processed = 0
            av_salary = 0
            for i, vacancy in enumerate(vacancies['items']):
                if predict_rub_salary(vacancy):
                    vacancies_processed += 1
                    av_salary += predict_rub_salary(vacancy)

            statistics_for_salary[languages[num]].update({'vacancies_processed': vacancies_processed})
            average_salary = int(av_salary / vacancies_processed)
            statistics_for_salary[languages[num]].update({'average_salary': average_salary})

    pprint(statistics_for_salary)

    params = {'text': 'программист Python', 'search_field': 'name', 'premium': True,
              'area': '1'}
    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancies = response.json()

    for vacancy in vacancies['items']:
        print(predict_rub_salary(vacancy))


if __name__ == '__main__':
    main()
