import re
from collections import Counter

class SpellingCorrector:
    def __init__(self, corpus_text):
        self.words = Counter(self._words(corpus_text))

    def _words(self, text):
        return re.findall(r'\w+', text.lower())

    def correction(self, word):
        candidates = self._candidates(word)
        return max(candidates, key=self.words.get)

    def _candidates(self, word):
        return (self._known([word]) or
                self._known(self._edits1(word)) or
                self._known(self._edits2(word)) or
                [word])

    def _known(self, words):
        return set(w for w in words if w in self.words)

    def _edits1(self, word):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word)+1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def _edits2(self, word):
        return (e2 for e1 in self._edits1(word) for e2 in self._edits1(e1))
