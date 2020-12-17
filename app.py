import os
import random
from flask import Flask, render_template, send_from_directory
import data


app = Flask(__name__)


# https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main():
    def get_promo_tours():
        """
        генерация списка туров для главной страницы
        """
        # отбираем список из 6ти случайных туров
        tours = {id: data.tours[id] for id in random.sample(data.tours.keys(), 6)}
        # сортируем их в порядке убывания звезд
        tours = {id: tour for id, tour in sorted(tours.items(), key=lambda x: int(x[1]['stars']), reverse=True)}
        return tours

    return render_template(
        'index.html',
        title=data.title,
        departures=data.departures,
        subtitle=data.subtitle,
        description=data.description,
        tours=get_promo_tours()
    )


@app.route('/departures/<departure>/')
def departures(departure):
    if departure not in data.departures.keys():
        return f"Код отправления '{departure}' не найден.", 404

    # первая буква в названии направления должна быть в нижнем регистре
    departure_patch = data.departures[departure][0].lower() + data.departures[departure][1:]

    return render_template(
        'departure.html',
        title=f'{data.title} - туры {departure_patch}',
        departures=data.departures,
        departure=departure_patch,
        tours={id: tour for id, tour in data.tours.items() if tour.get('departure', None) == departure}
    )


@app.route('/tours/<int:id>/')
def tours(id):
    tour = data.tours.get(id, None)
    if tour is None:
        return f'Тур id={id} не найден', 404

    # первая буква в названии направления должна быть в нижнем регистре
    departure = tour['departure']
    departure_patch = data.departures[departure][0].lower() + data.departures[departure][1:]

    return render_template(
        'tour.html',
        title=f'{data.title} - {tour["title"]}',
        departures=data.departures,
        departure=departure_patch,
        tour=tour
    )


@app.route('/data/')
def get_tours():
    # return 'список всех туров'
    response = ['<h1>Все туры:</h1>']

    for id, tour in data.tours.items():
        response.append(f'<p>{tour["country"]}: <a href="/data/tours/{id}/">{tour["title"]} {tour["price"]} {tour["stars"]}* </a></p>')

    return ' '.join(response)


@app.route('/data/departures/<departure>')
def get_tour_by_departure(departure):
    # return 'туры по направлению'
    if departure not in data.departures.keys():
        return f"Код отправления '{departure}' не найден.", 404

    response = [f'<h1>Туры по направлению {data.departures[departure]}:</h1>']
    for id, tour in {id: t for id, t in data.tours.items() if t['departure'] == departure}.items():
        response.append(f'<p>{tour["country"]}: <a href="/data/tours/{id}/">{tour["title"]} {tour["price"]} {tour["stars"]}* </a></p>')

    return ' '.join(response)


@app.route('/data/tours/<int:id>/')
def get_tour_by_id(id):
    # return 'тур по id'
    tour = data.tours.get(id, None)
    if tour is None:
        return f'Тур id={id} не найден', 404

    response = [
        f'<h1>{tour["country"]}: {tour["title"]} {tour["price"]}:</h1>',
        f'<p>{tour["nights"]} ночей</p>',
        f'<p>Стоимость: {tour["price"]} Р</p>',
        f'<p>{tour["description"]}</p>'
    ]

    return ' '.join(response)


if __name__ == '__main__':
    app.run()
