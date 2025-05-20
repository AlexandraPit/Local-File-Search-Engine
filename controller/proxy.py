class ProxySearch:
    def __init__(self, real_engine):
        self.real_engine = real_engine
        self.cache = {}

    def search(self, query):
        if query in self.cache:
            print(f"[CACHE HIT] Returning cached results for: '{query}'")
            return self.cache[query]

        print(f"[CACHE MISS] Performing search for: '{query}'")
        results = self.real_engine.search(query)
        self.cache[query] = results
        return results

    def clear_cache(self):
        self.cache.clear()

    def index_directory(self, path):
        self.real_engine.index_directory(path)
        self.cache.clear()

    def get_preview(self, path):
        return self.real_engine.get_preview(path)

    def cleanup(self):
            self.real_engine.cleanup()
