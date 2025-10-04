import datetime
import pandas
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape


def declination_of_year(years):
    years = str(years)

    numbers_v1 = ['2', '3', '4']
    numbers_v2 = ['5', '6', '7', '8', '9']

    if len(years) == 1:
        # Если число состоит из одной цифры
        if years == '1':
            return 'год'
        elif years in numbers_v1:
            return 'года'
        elif years in numbers_v2:
            return 'лет'
    elif len(years) == 2:
        # Если число состоит из двух цифр
        if years == '11' or years[1] == '0':
            return 'лет'
        elif years[1] == '1':
            return 'год'
        elif years[1] in numbers_v1:
            return 'года'
        elif years[1] in numbers_v2:
            return 'лет'
    elif len(years) > 2:
        # Если в числе больше двух цифр
        years = years[-2] + years[-1]
        if years == '00' or years == '11' or years[1] == '0':
            return 'лет'
        elif years[1] == '1':
            return 'год'
        elif years[1] in numbers_v1:
            return 'года'
        elif years[1] in numbers_v2:
            return 'лет'


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    date_of_creation = datetime.datetime(year=1920,month=1,day=1)
    now = datetime.datetime.now()
    age = now - date_of_creation
    age = age.days // 365
    declension = declination_of_year(age)
    age_text = f'Уже {age} {declension} с вами'

    excel_data = pandas.read_excel(
        'wine3.xlsx',
        na_values=None,
        keep_default_na=False,
        )

    grouped_products = {}
    for category, group in excel_data.groupby('Категория'):
        grouped_products[category] = group.to_dict('records')

    assortment = []

    for key, value in grouped_products.items():
        category = {}
        category['category'] = key
        products = []
        for product in value:
            data = {}
            data['title'] = product['Название']
            data['variety'] = product['Сорт']
            data['price'] = product['Цена']
            data['image'] = product['Картинка']
            data['stock'] = product['Акция']
            products.append(data)
        category['products'] = products
        assortment.append(category)

    other_page = {'year': age_text}

    rendered_page = template.render(assortment=assortment, other_page=other_page)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()