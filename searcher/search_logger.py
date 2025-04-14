from collections import Counter

from searcher.Observer import Observer


class SearchLogger(Observer):
    def __init__(self):
        self.history = []

    def update(self, query):
        self.history.append(query)
        print(f"SearchLogger: logged query '{query}'")

    def get_suggestions(self, prefix):
        return [q for q in self.history if q.startswith(prefix)]

    def get_frequent_terms(self, top_n=5):
        all_terms = []
        for query in self.history:
            # Simple split, or use regex for better tokenizing
            terms = query.lower().split()
            all_terms.extend(terms)

        counter = Counter(all_terms)
        return [term for term, _ in counter.most_common(top_n)]

    def rank_results(self, query, results):
        frequent_terms = self.get_frequent_terms()

        def score(result):
            path = result[0].lower()
            hits = sum(term in path for term in frequent_terms)
            return hits

        ranked = sorted(results, key=score, reverse=True)
        return ranked

