import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parent
SQLITE_BACKUP = ROOT / "cinemaverse.db"
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "cinemaverse")
if os.environ.get("VERCEL") == "1" and "MONGODB_URI" not in os.environ:
    mongo_client = None
else:
    mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
reviews_collection = None
SEED_REVIEWS = [
    {
        "movie_name": "Dragon",
        "language": "Tamil",
        "year": 2025,
        "rating": 4.2,
        "review": "Pradeep Ranganathan turns a college student's spectacularly bad decisions into a brisk comedy about growing up. The jokes land best when the film lets its bruised, unexpectedly sincere lead show through.",
    },
    {
        "movie_name": "Tourist Family",
        "language": "Tamil",
        "year": 2025,
        "rating": 4.5,
        "review": "A gentle family comedy that finds humor and warmth in the strain of starting over somewhere new. Sasikumar and Simran make the family's affection feel natural, giving its hopeful story a grounded emotional pull.",
    },
    {
        "movie_name": "Thudarum",
        "language": "Malayalam",
        "year": 2025,
        "rating": 4.5,
        "review": "Mohanlal anchors this patient family thriller with a performance that moves from everyday warmth to simmering resolve. Its unhurried opening gives the later tension room to build, and the emotional stakes stay personal throughout.",
    },
    {
        "movie_name": "Lokah Chapter 1: Chandra",
        "language": "Malayalam",
        "year": 2025,
        "rating": 4.3,
        "review": "A stylish, atmospheric opening to a Malayalam superhero world, led by Kalyani Priyadarshan's focused performance. The urban fantasy feels rooted in local texture, even when its ambitious world-building occasionally slows the momentum.",
    },
    {
        "movie_name": "Court: State vs a Nobody",
        "language": "Telugu",
        "year": 2025,
        "rating": 4.4,
        "review": "A clear-eyed courtroom drama that turns a young couple's case into a pointed look at power and unequal justice. The measured direction and persuasive performances keep its social argument grounded in recognizable human stakes.",
    },
    {
        "movie_name": "Sankranthiki Vasthunam",
        "language": "Telugu",
        "year": 2025,
        "rating": 4.0,
        "review": "A broad, knowingly playful family entertainer that leans on Venkatesh's comic timing and a lively domestic triangle. The humor is deliberately uncomplicated, and the film is most enjoyable when it embraces that easygoing spirit.",
    },
    {
        "movie_name": "Kantara: Chapter 1",
        "language": "Kannada",
        "year": 2025,
        "rating": 4.2,
        "review": "Rishab Shetty expands the saga with striking landscape imagery and a deep investment in folklore and ritual. Its scale is impressive, while the most affecting passages remain those tied to community, belief, and the land.",
    },
    {
        "movie_name": "Retro",
        "language": "Tamil",
        "year": 2025,
        "rating": 3.8,
        "review": "A visually assured romantic action drama with a distinctive period mood and committed performances from Suriya and Pooja Hegde. Its shifting tones do not always settle neatly, but the film's sincerity and imagery leave a clear impression.",
    },
]


def initialize_database():
    global reviews_collection
    if mongo_client is None:
        raise RuntimeError("Set MONGODB_URI in the Vercel project environment variables.")
    reviews_collection = mongo_client[MONGODB_DATABASE]["reviews"]
    if reviews_collection.count_documents({}):
        return

    initial_reviews = []
    if SQLITE_BACKUP.exists():
        try:
            with sqlite3.connect(SQLITE_BACKUP) as connection:
                connection.row_factory = sqlite3.Row
                initial_reviews = [
                    dict(row)
                    for row in connection.execute(
                        "SELECT movie_name, language, year, rating, review FROM reviews"
                    )
                ]
        except sqlite3.Error:
            initial_reviews = []

    if not initial_reviews:
        initial_reviews = SEED_REVIEWS

    now = datetime.now(timezone.utc)
    reviews_collection.insert_many(
        [{**review, "created_at": now} for review in initial_reviews]
    )


def get_reviews():
    documents = reviews_collection.find().sort("_id", -1)
    return [
        {
            "id": str(document["_id"]),
            "movie_name": document["movie_name"],
            "language": document["language"],
            "year": document["year"],
            "rating": document["rating"],
            "review": document["review"],
            "created_at": document["created_at"].isoformat(),
        }
        for document in documents
    ]


def save_review(payload):
    movie_name = str(payload.get("movie_name", "")).strip()
    language = str(payload.get("language", "")).strip()
    review = str(payload.get("review", "")).strip()
    year = int(payload.get("year", 0))
    rating = float(payload.get("rating", 0))
    if not movie_name or len(movie_name) > 120:
        raise ValueError("Movie name must be between 1 and 120 characters")
    if not language or len(language) > 40:
        raise ValueError("Language must be between 1 and 40 characters")
    if not review or len(review) > 2000:
        raise ValueError("Review must be between 1 and 2000 characters")
    if year < 1888 or year > 2100:
        raise ValueError("Enter a valid release year")
    if rating < 0 or rating > 5:
        raise ValueError("Rating must be between 0 and 5")

    result = reviews_collection.insert_one(
        {
            "movie_name": movie_name,
            "language": language,
            "year": year,
            "rating": rating,
            "review": review,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return str(result.inserted_id)
