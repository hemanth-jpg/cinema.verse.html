import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

from pymongo.errors import PyMongoError

from database import get_reviews, initialize_database, mongo_client, save_review


class handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlsplit(self.path).path != "/api/movies":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            mongo_client.admin.command("ping")
            initialize_database()
            self.send_json(200, get_reviews())
        except PyMongoError as error:
            self.send_json(503, {"error": f"MongoDB is unavailable: {error}"})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/movies":
            self.send_json(404, {"error": "Not found"})
            return
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 10000:
            self.send_json(413, {"error": "Review is too large"})
            return
        try:
            payload = json.loads(self.rfile.read(content_length))
            mongo_client.admin.command("ping")
            initialize_database()
            review_id = save_review(payload)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error) or "Invalid review data"})
            return
        except PyMongoError as error:
            self.send_json(503, {"error": f"MongoDB is unavailable: {error}"})
            return
        self.send_json(201, {"id": review_id, "message": "Review saved"})

    def log_message(self, format, *args):
        pass
