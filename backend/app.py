from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo import TEXT
from bson import ObjectId
from sentence_transformers import SentenceTransformer
import numpy as np

from generator import converse_with_llm

from apiKey import MONGO_CONNECTION_STRING

from flask_cors import CORS
import spacy
import logging

logging.basicConfig(level=logging.INFO)


client = MongoClient(MONGO_CONNECTION_STRING)
db = client["movie_app"]
movies_collection = db["movies"]
history_collection = db["search_history"]


nlp = spacy.load("en_core_web_sm")

model = SentenceTransformer("all-MiniLM-L6-v2")

app = Flask(__name__)
CORS(app)

GENRE_SYNONYMS = {
    "romance": ["romance", "romantic", "love", "rom-com"],
    "action": ["action", "adventure", "fight", "combat"],
    "comedy": ["comedy", "funny", "humor", "satire"],
    "horror": ["horror", "scary", "thriller", "fear"],
    "sci-fi": ["sci-fi", "science fiction", "space", "alien"],
}


def parse_advanced_filters(query):
    """
    Parse the query to extract advanced filters for movie search.

    Args:
        query (str): User input query.

    Returns:
        dict: Filters like minimum rating or vote count.
    """
    filters = {}

    if "top" in query.lower() or "high-rated" in query.lower():
        filters["vote_average"] = {"$gte": 8.5}

    if "popular" in query.lower():
        filters["vote_count"] = {"$gte": 500}

    if "recent" in query.lower():
        filters["release_date"] = {"$gte": "2020-01-01"}

    if "old" in query.lower():
        filters["release_date"] = {"$lte": "2000-01-01"}

    return filters


def clean_document(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def retrieve_similar_movies(query, n=5):
    """
    Retrieve similar movies based on vector similarity.

    Args:
        query (str): User input query.
        n (int): Number of similar movies to retrieve.

    Returns:
        list: List of similar movies with metadata.
    """
    query_embedding = model.encode(query).tolist()

    filters = parse_advanced_filters(query)

    # Perform vector similarity search
    similar_movies_search = movies_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "movie_index",
                    "queryVector": query_embedding,
                    "path": "movie_embedding",
                    "k": n,
                    "numCandidates": 1000,
                    "limit": 20,
                }
            },
            {"$match": filters},
            {
                "$project": {
                    "title": 1,
                    "overview": 1,
                    "poster_path": 1,
                    "vote_average": 1,
                    "vote_count": 1,
                    "release_date": 1,
                    "score": {"$meta": "searchScore"},
                }
            },
        ]
    )

    similar_movies = [clean_document(movie) for movie in similar_movies_search]
    return similar_movies


def retrieve_similar_movies_by_genre(genre, n=150, query=""):
    filters = parse_advanced_filters(query)
    filters["genre_names"] = {"$regex": f"^{genre}", "$options": "i"}  # Match genre

    matching_movies = (
        movies_collection.find(
            filters,
            {
                "title": 1,
                "overview": 1,
                "poster_path": 1,
                "vote_average": 1,
                "vote_count": 1,
                "release_date": 1,
                "genre_names": 1,
            },
        )
        .sort("popularity", -1)
        .limit(n)
    )

    similar_movies = [clean_document(movie) for movie in matching_movies]
    return similar_movies


def process_query(query):
    doc = nlp(query)
    keywords = [chunk.text.lower() for chunk in doc.noun_chunks] + [
        token.text.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop
    ]
    return list(set(keywords))


def match_genre(keywords):
    for keyword in keywords:
        for genre, synonyms in GENRE_SYNONYMS.items():
            if keyword.lower() in synonyms:
                return genre
    return None


@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data.get("query", "")
    input_prompt = process_query(query)

    existing_entry = history_collection.find_one({"query": query})
    if existing_entry:
        return jsonify(existing_entry["result"])

    genre_match = match_genre(input_prompt)

    if genre_match:
        similar_movies = retrieve_similar_movies_by_genre(genre_match)
    else:
        cleaned_query = " ".join(input_prompt)
        similar_movies = retrieve_similar_movies(cleaned_query)

    similar_movie_info = "\n".join([f"{movie['title']}" for movie in similar_movies])

    prompt = f"""
    Recommend a movie similar to: {similar_movie_info}
    based on user's query :{query}
    and explain why """

    recommendation = converse_with_llm(prompt)

    result = {"similar_movies": similar_movies, "recommendation": recommendation}

    if len(similar_movies) > 0:
        history_collection.insert_one({"query": query, "result": result})

    return jsonify(result)


@app.route("/api/history", methods=["GET"])
def get_history():
    """
    Fetches all previous search queries and their results.
    """
    history = history_collection.find({}, {"_id": 0, "query": 1})
    return jsonify([entry["query"] for entry in history])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
