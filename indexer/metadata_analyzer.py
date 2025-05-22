from collections import Counter
from pathlib import Path
from datetime import datetime

class ResultMetadataAnalyzer:
    def __init__(self, results):
        self.results = results

    def summarize_file_types(self):
        exts = [Path(r["path"]).suffix.lower() for r in self.results]
        return Counter(exts)

    def summarize_modified_years(self):
        years = [r["modified_time"].year for r in self.results if r.get("modified_time")]
        return Counter(years)

    def summarize_languages(self):
        # You can infer based on extension
        ext_to_lang = {
            ".py": "Python", ".java": "Java", ".c": "C", ".cpp": "C++",
            ".js": "JavaScript", ".html": "HTML", ".css": "CSS"
        }
        langs = [
            ext_to_lang.get(Path(r["path"]).suffix.lower(), "Unknown")
            for r in self.results
        ]
        return Counter(langs)
