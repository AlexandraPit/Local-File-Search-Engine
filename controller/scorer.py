import os
import time

class ScoreCalculator:
    def rank_files(self, files, frequent_terms):
        ranked = []
        for file in files:
            score = self.calculate_score(file, frequent_terms)
            ranked.append((file[0], score))
        return sorted(ranked, key=lambda x: x[1], reverse=True)

    def calculate_score(self, file_data, frequent_terms):
        score = 0
        path = file_data[0]
        extension = file_data[2]

        # Decrease score based on path length (longer paths have lower scores)
        score -= len(path)

        # If "writing" is found in the path, boost score
        if "writing" in path:
            score += 3

        # Boost score if any frequent terms are found in the path
        if any(term in path for term in frequent_terms):
            score += 2

        # Prioritize specific file extensions
        prioritized_extensions = [".txt", ".docx"]
        if extension in prioritized_extensions:
            score += 5

        # Check recent file access time
        try:
            access_time = os.path.getatime(path)
            if (time() - access_time) < 3600 * 24:  # modified time
                score += 3
        except:
            pass

        # Decrease score based on file size (larger files have lower scores)
        try:
            file_size = os.path.getsize(path)
            score -= file_size / 1000
        except:
            pass
        return score

