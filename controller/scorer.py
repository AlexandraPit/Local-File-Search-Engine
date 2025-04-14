class ScoreCalculator:
    def rank_files(self, files, frequent_terms):
        ranked = []
        for file in files:
            score = self.calculate_score(file, frequent_terms)
            ranked.append((file[0], score))
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def calculate_score(self, file_data, frequent_terms):
        path = file_data[0].lower()
        score = sum(1 for term in frequent_terms if term in path)
        return score
