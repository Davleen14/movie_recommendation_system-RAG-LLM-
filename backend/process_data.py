import requests
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

from apiKey import TMDB_API_KEY, MONGO_CONNECTION_STRING
import logging

logging.basicConfig(level=logging.INFO)

client = MongoClient(MONGO_CONNECTION_STRING)
db = client["movie_app"]
movies_collection = db["movies"]
TMDB_API_KEY = TMDB_API_KEY
model = SentenceTransformer("all-MiniLM-L6-v2")


def fetch_tmdb_genres():

    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        logging.info("Fetched genres from TMDB.")
        genres = response.json().get("genres", [])
        return {genre["id"]: genre["name"] for genre in genres}
    else:
        logging.error(f"Failed to fetch genres from TMDB: {response.status_code}")
        return {}


def fetch_tmdb_movies(page=1):

    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": TMDB_API_KEY, "language": "en-US", "page": page}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        logging.info(f"Fetched movies from TMDB (page {page}).")
        movies = response.json().get("results", [])
        filtered_movies = [movie for movie in movies if not movie.get("adult", False)]
        return filtered_movies
    else:
        logging.error(f"Failed to fetch movies from TMDB: {response.status_code}")
        return []


def seed_movies(movies, genres):
    for movie in movies:
        genre_ids = movie.get("genre_ids", [])
        genre_names = [genres[genre_id] for genre_id in genre_ids if genre_id in genres]
        genre_text = ", ".join(genre_names)
        logging.info(f"genre_text {genre_text}.")

        movie_text = f"{movie['title']} {movie.get('overview', '')}"
        movie_embedding = model.encode(movie_text)

        movie_doc = {
            "tmdb_id": movie["id"],
            "title": movie["title"],
            "overview": movie.get("overview", ""),
            "release_date": movie.get("release_date", ""),
            "popularity": movie.get("popularity", 0),
            "poster_path": movie.get("poster_path", ""),
            "vote_average": movie.get("vote_average", 0),
            "vote_count": movie.get("vote_count", 0),
            "genre_ids": genre_ids,
            "genre_names": genre_names,
            "movie_embedding": movie_embedding.tolist(),
        }

        movies_collection.update_one(
            {"tmdb_id": movie["id"]}, {"$set": movie_doc}, upsert=True
        )


def seed_database_from_tmdb(pages=1):

    genres = fetch_tmdb_genres()

    for page in range(1, pages + 1):
        logging.info(f"Inserted Page number: {page}")

        movies = fetch_tmdb_movies(page)
        if not movies:
            break
        seed_movies(movies, genres)


seed_database_from_tmdb(pages=500)
print("Database seeding completed!")
