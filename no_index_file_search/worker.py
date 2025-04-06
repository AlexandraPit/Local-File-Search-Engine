import os

from flask import Flask, request, jsonify


def start_worker(root_dir, port):
    worker = Worker(root_dir, port)
    worker.run()


class Worker:
    def __init__(self, root_dir, port):
        self.root_dir = root_dir
        self.port = port
        self.app = Flask(__name__)
        self.app.add_url_rule("/api/search", "search", self.search, methods=["POST"])

    def search_files(self, query, root_dir):
        print(f"[WORKER {self.port}] Searching in: {root_dir} for '{query}'", flush=True)
        matches = []
        print(f"Searching in {root_dir} for {query}", flush=True)

        for root, _, files in os.walk(root_dir):
            print(f"Checking directory: {root}")  # Debugging line
            for file in files:
                print(f"Found file: {file}")  # Debugging line
                if query.lower() in file.lower():
                    matches.append(os.path.join(root, file))

        print(f"Matches found: {matches}")  # Debugging line
        return matches

    def search(self):
        data = request.get_json()
        query = data.get("query", "")
        if not query:
            return jsonify({"error": "No query provided"}), 400

        result = self.search_files(query, self.root_dir)

        return jsonify({"results": result})

    def run(self):
        print(f"[WORKER {self.port}] Flask starting on port {self.port}...", flush=True)
        self.app.run(port=self.port, debug=False, use_reloader=False)
