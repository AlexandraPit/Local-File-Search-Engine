from spelling_corrector.spelling_corrector import SpellingCorrector
from spelling_corrector.query_corrector import NorvigSpellingCorrector
from spelling_corrector.query_corrector import LoggingCorrectorDecorator

class SpellingCorrectionFacade:
    def __init__(self, corpus_path="data/big.txt"):
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus_text = f.read()

        base_corrector = SpellingCorrector(corpus_text)
        strategy = NorvigSpellingCorrector(base_corrector)
        decorated = LoggingCorrectorDecorator(strategy)
        self.corrector = decorated

    def correct(self, query: str) -> str:
        return self.corrector.correct(query)
