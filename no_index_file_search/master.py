import requests
from flask import Flask, request, jsonify


class Master:
    def __init__(self, worker_endpoints):
        self.worker_endpoints = worker_endpoints
        self.cache = {}
        self.app = Flask(__name__)
        self.app.add_url_rule("/api/search", "search", self.search, methods=["POST"])

    def query_workers(self, query):
        results = []
        for worker_url in self.worker_endpoints:
            try:
                response = requests.post(worker_url, json={"query": query})
                if response.status_code == 200:
                    results.extend(response.json().get("results", []))
            except requests.RequestException:
                continue
        return sorted(results)

    def search(self):
        data = request.get_json()
        query = data.get("query", "")
        if not query:
            return jsonify({"error": "No query provided"}), 400

        if query in self.cache:
            return jsonify({"results": self.cache[query], "cached": True})

        results = self.query_workers(query)
        self.cache[query] = results
        return jsonify({"results": results, "cached": False})

    def run(self):
        self.app.run(port=3000, debug=False, use_reloader=False)