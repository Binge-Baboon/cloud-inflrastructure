import json
import boto3
from shared.utils import create_response
import heapq

ranking = {
    "genres": {

    },
    "actors": {

    },
    "directors": {

    }
}

movies_ranking = {

}

tvshows_ranking = {

}

def generate(event, context):
    dynamodb = boto3.resource('dynamodb')
    user_table = dynamodb.Table('Users')
    movies_table = dynamodb.Table('Movies')
    tvshows_table = dynamodb.Table('TvShows')

    email = event['pathParameters']['email']
    user = user_table.get_item(
        Key={
            'email': email
        }
    )['Item']

    watched_movies = user['watched']['movies']
    watched_tvShows = user['watched']['tvShows']
    downloads_movies = user['downloads']['movies']
    downloads_tvShows = user['downloads']['tvShows']
    rated_movies = user.get('movieRatings', {})
    rated_tvshows = user.get('tvShowRatings', {})

    ranking = {"genres": {}, "actors": {}, "directors": {}}
    movies_ranking = {}
    tvshows_ranking = {}
    calculate_ranking(watched_movies, movies_table, user, ranking)
    calculate_ranking(watched_tvShows, tvshows_table, user, ranking)
    calculate_ranking(downloads_movies, movies_table, user, ranking)
    calculate_ranking(downloads_tvShows, tvshows_table, user, ranking)
    calculate_review_ranking(rated_movies, movies_table, user, ranking)
    calculate_review_ranking(rated_tvshows, tvshows_table, user, ranking)

    response = movies_table.scan()
    movies = response.get('Items', [])
    response = tvshows_table.scan()
    tvshows = response.get('Items', [])

    for movie in movies:
        evaluate_item(movie, movies_ranking, ranking)

    for tvshow in tvshows:
        evaluate_item(tvshow, tvshows_ranking, ranking)

    top_ten_movies = heapq.nlargest(10, movies_ranking, key=movies_ranking.get)
    top_ten_tvshows = heapq.nlargest(10, tvshows_ranking, key=tvshows_ranking.get)

    return create_response(200, {"movies_ranking": movies_ranking, "tvshows_rankings": tvshows_ranking, "movies": top_ten_movies, "tvshows": top_ten_tvshows})


def calculate_ranking(contents, table, user, ranking):
    points = 10
    i = len(contents)-1
    while points > 0 and i > -1:
        content_response = table.get_item(Key={'id': contents[i]})
        content = content_response.get('Item', None)
        if content is not None:
            rank_content(content, points, user, ranking)
        points -= 1
        i -= 1


def calculate_review_ranking(contents, table, user, ranking):
    for key, value in contents.items():
        content_response = table.get_item(Key={'id': key})

        content = content_response.get('Item', None)
        if content is None:
            continue
        rank_content(content, 5, user, ranking, value)


def rank_content(content, points, user, ranking, rating=3):
    rating = float(rating)
    for genre in content.get('genres', []):
        ranking["genres"].setdefault(genre, 0)
        if genre in user.get("subscribed", {}).get('genres', []):
            ranking["genres"][genre] += points * (rating - 2)
        else:
            ranking["genres"][genre] += (points / 3) * (rating - 2)

    for actor in content.get('actors', []):
        ranking["actors"].setdefault(actor, 0)
        if actor in user.get("subscribed", {}).get('actors', []):
            ranking["actors"][actor] += points * (rating - 2)
        else:
            ranking["actors"][actor] += (points / 3) * (rating - 2)

    for director in content.get('directors', []):
        ranking["directors"].setdefault(director, 0)
        if director in user.get("subscribed", {}).get('directors', []):
            ranking["directors"][director] += points * (rating - 2)
        else:
            ranking["directors"][director] += (points / 3) * (rating - 2)


def evaluate_item(item, item_ranking, ranking):
    item_ranking.setdefault(item["id"], 0)
    for genre in item.get('genres', []):
        item_ranking[item["id"]] += ranking["genres"].get(genre, 0)
    for actor in item.get('actors', []):
        item_ranking[item["id"]] += ranking["actors"].get(actor, 0)
    for director in item.get('directors', []):
        item_ranking[item["id"]] += ranking["directors"].get(director, 0)
