from collections import Counter
from controller.scorer import ScoreCalculator
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



