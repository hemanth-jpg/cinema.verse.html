import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pymongo.errors import PyMongoError
from database import MONGODB_DATABASE, MONGODB_URI, get_reviews, initialize_database, mongo_client, save_review

ROOT = Path(__file__).resolve().parent
class CinemaVerseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/movies":
            try:
                self.send_json(200, get_reviews())
            except PyMongoError as error:
                self.send_json(503, {"error": f"MongoDB is unavailable: {error}"})
            return
        if self.path == "/":
            self.path = "/cinemaverse.html"
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/movies":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 10000:
                self.send_json(413, {"error": "Review is too large"})
                return
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict):
                raise ValueError("Review data must be an object")
            review_id = save_review(payload)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error) or "Invalid review data"})
            return

        except PyMongoError as error:
            self.send_json(503, {"error": f"MongoDB is unavailable: {error}"})
            return
        self.send_json(201, {"id": review_id, "message": "Review saved"})

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    try:
        mongo_client.admin.command("ping")
        initialize_database()
        server = ThreadingHTTPServer(("127.0.0.1", 8000), CinemaVerseHandler)
    except PyMongoError as error:
        print(f"Could not connect to MongoDB at {MONGODB_URI}: {error}")
        print("Start MongoDB Community Server and verify MONGODB_URI.")
        raise SystemExit(1) from error
    print(
        f"CinemaVerse running at http://127.0.0.1:8000 "
        f"(MongoDB: {MONGODB_DATABASE}.reviews)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCinemaVerse server stopped")
    finally:
        server.server_close()
        mongo_client.close()
