import os
import time

class ScoreCalculator:
    def rank_files(self, files, frequent_terms):
        ranked = []
        for item in files:
            path = item["path"]
            extension = item["extension"]

            score = self.calculate_score(path, extension, frequent_terms)
            item["score"] = score
            ranked.append(item)

        return sorted(ranked, key=lambda x: x["score"], reverse=True)



    def calculate_score(self, path, extension, frequent_terms):
        score = 0
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
            if (time.time() - access_time) < 3600 * 24:
                score += 3
        except:
            pass

        try:
            file_size = os.path.getsize(path)
            score -= file_size / 1000
        except:
            pass
        return score

