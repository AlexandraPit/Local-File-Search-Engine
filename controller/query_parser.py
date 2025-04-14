import re

class QueryParser:
    def parse_query(self, query):
        pattern = r'(path|content):([^\s]+)'
        matches = re.findall(pattern, query)
        query_dict = {}

        for qualifier, value in matches:
            query_dict.setdefault(qualifier, []).append(value)

        if not matches and query.strip():
            query_dict['general'] = query.strip().split()

        return query_dict

    def process_query(self, query_dict):
        query_parts = []
        for qualifier, values in query_dict.items():
            if qualifier in {"path", "content"}:
                query_parts.append(f"({' AND '.join(values)})")
        return " AND ".join(query_parts)
