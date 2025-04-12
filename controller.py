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

    def index_directory(self, path):
        crawl_and_index(path, **self.db)

    def search(self, query):
        if not query.strip():
            return []
        return search_files(query, **self.db)

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
        """
        Parses the query string and returns a dictionary with qualifiers.
        """
        # Define regex pattern to capture 'path' and 'content' qualifiers.
        pattern = r'(path|content):([^\s]+)'

        # Find all matches using regex
        matches = re.findall(pattern, query)

        query_dict = {}

        # Process matches and add them to the dictionary
        for qualifier, value in matches:
            # If the qualifier already exists, append the new value to the list.
            if qualifier in query_dict:
                query_dict[qualifier].append(value)
            else:
                query_dict[qualifier] = [value]

        return query_dict

    def process_query(self, query_dict):
        """
        Processes the parsed query dictionary to combine duplicate qualifiers
        with 'AND' and prepare the query for searching.
        """
        query_parts = []

        # For each qualifier (path, content), combine values with 'AND'
        for qualifier, values in query_dict.items():
            if qualifier == "path":
                query_parts.append(f"({' AND '.join(values)})")  # Combine path terms with AND
            elif qualifier == "content":
                query_parts.append(f"({' AND '.join(values)})")  # Combine content terms with AND

        # Join all parts with 'AND' to combine path and content conditions
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

        # Process duplicates by combining them with AND
        processed_query = self.process_query(parsed_query)

        print("Processed query:", processed_query)

        # You can now proceed to run the query against your database or file system
        # Example: Running a SQL query or filtering files


    def search_files(self, query):
        parsed_query = self.parse_query(query)
        matching_files = self.find_matching_files(parsed_query)

        scored_files = []
        for file in matching_files:
            score = self.calculate_file_score(file, parsed_query)
            scored_files.append((file, score))

        scored_files.sort(key=lambda x: x[1], reverse=True)  # Sort by score
        return scored_files

