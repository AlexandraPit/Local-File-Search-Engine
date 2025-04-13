from indexer import crawl_and_index
from searcher import search_files
from preview import get_file_preview, is_txt_file
from database import clear_database
from config import DB_CONFIG
from db_utils import connect_to_db

import re

class Controller:
    def __init__(self):
        self.db = DB_CONFIG
        self.observers = []

    def index_directory(self, path):
        crawl_and_index(path, **self.db)

    def search(self, query):
        if not query.strip():
            return []

        self.notify_observers(query)  # 🔔 Log query activity

        parsed = self.parse_query(query)
        raw_results = search_files(parsed, **self.db)

        # Check if any observer provides frequent terms
        frequent_terms = []
        for observer in self.observers:
            if hasattr(observer, "get_frequent_terms"):
                frequent_terms = observer.get_frequent_terms()
                break  # just get from the first logger-like observer

        # Rank the results using the frequent terms
        ranked_results = []
        for file in raw_results:
            score = self.calculate_file_score(file, frequent_terms)
            ranked_results.append((file[0], score))  # file[0] = path

        ranked_results.sort(key=lambda x: x[1], reverse=True)
        return ranked_results

    def get_preview(self, path):
        if is_txt_file(path, **self.db):
            return get_file_preview(path, **self.db)
        return "(No preview)"

    def cleanup(self):
        conn = connect_to_db(**self.db)
        if conn:
            clear_database(conn)
            conn.close()

    def parse_query(self, query):
        pattern = r'(path|content):([^\s]+)'
        matches = re.findall(pattern, query)

        query_dict = {}

        for qualifier, value in matches:
            if qualifier in query_dict:
                query_dict[qualifier].append(value)
            else:
                query_dict[qualifier] = [value]

        # If no qualifiers were found, assume general search => search by name and content
        if not matches and query.strip():
            query_dict['general'] = query.strip().split()

        return query_dict

    def process_query(self, query_dict):
        query_parts = []
        for qualifier, values in query_dict.items():
            if qualifier == "path":
                query_parts.append(f"({' AND '.join(values)})")  # Combine path terms with AND
            elif qualifier == "content":
                query_parts.append(f"({' AND '.join(values)})")  # Combine content terms with AND

        return " AND ".join(query_parts)

    def handle_query(self, query):
        """
        Handles the query by parsing it, processing duplicates, and printing the final query.
        """
        parsed_query = self.parse_query(query)

        # Handle case for empty query or no valid qualifiers
        if not parsed_query:
            print("No valid qualifiers found in query.")
            return

        processed_query = self.process_query(parsed_query)

        print("Processed query:", processed_query)



    def search_files(self, query):
        parsed_query = self.parse_query(query)
        matching_files = self.find_matching_files(parsed_query)

        scored_files = []
        for file in matching_files:
            score = self.calculate_file_score(file, parsed_query)
            scored_files.append((file, score))

        scored_files.sort(key=lambda x: x[1], reverse=True)  # Sort by score
        return scored_files


    def register_observer(self, observer):
        self.observers.append(observer)


    def notify_observers(self, query):
        for observer in self.observers:
            observer.update(query)

    def calculate_file_score(self, file_data, frequent_terms):
        """
        file_data is a tuple, with file_data[0] being the path.
        Adds score if the file path contains frequent search terms.
        """
        path = file_data[0].lower()
        score = 0

        for term in frequent_terms:
            if term in path:
                score += 1  # you can tweak this weight

        return score

