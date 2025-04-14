from controller.query_parser import QueryParser
from controller.scorer import ScoreCalculator
from controller.observer_manager import ObserverManager
from indexer.indexer import crawl_and_index
from searcher.searcher import search_files
from previewer.preview import get_file_preview
from previewer.file_type_checker import is_txt_file
from database.maintain_db import clear_database
from database.config import DB_CONFIG
from database.db_utils import connect_to_db

class Controller:
    def __init__(self):
        self.db = DB_CONFIG
        self.parser = QueryParser()
        self.scorer = ScoreCalculator()
        self.observer_manager = ObserverManager()

    def index_directory(self, path):
        crawl_and_index(path, **self.db)

    def search(self, query):
        if not query.strip():
            return []

        parsed = self.parser.parse_query(query)
        raw_results = search_files(parsed, **self.db)

        frequent_terms = self.observer_manager.get_frequent_terms()

        ranked_results = self.scorer.rank_files(raw_results, frequent_terms)
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

    def register_observer(self, observer):
        self.observer_manager.register(observer)
