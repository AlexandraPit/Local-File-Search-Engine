class QueryCorrectionStrategy:
    def correct(self, query: str) -> str:
        raise NotImplementedError()

class NorvigSpellingCorrector(QueryCorrectionStrategy):
    def __init__(self, spelling_corrector):
        self.spelling_corrector = spelling_corrector

    def correct(self, query: str) -> str:
        corrected_words = []
        for word in query.split():
            corrected_words.append(self.spelling_corrector.correction(word))
        return " ".join(corrected_words)

class LoggingCorrectorDecorator(QueryCorrectionStrategy):
    def __init__(self, wrapped_corrector):
        self.wrapped_corrector = wrapped_corrector

    def correct(self, query: str) -> str:
        corrected = self.wrapped_corrector.correct(query)
        print(f"[LOG] Corrected '{query}' to '{corrected}'")
        return corrected

