import json
from datetime import datetime
from indexer import report_setup


def save_index_report(file_data, errors=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entries = [
        f"Indexing started at {timestamp}",
        f"Indexed {len(file_data)} files.",
        f"Indexing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]

    if errors:
        log_entries.append("Errors during indexing:")
        log_entries.extend(errors)

    if report_setup.REPORT_FORMAT == "json":
        save_json_report(file_data, log_entries)
    elif report_setup.REPORT_FORMAT == "text":
        save_text_report(file_data, log_entries)

def save_json_report(file_data, log_entries):
    report_data = {
        "log": log_entries,
        "files": [
            {"path": row[0], "name": row[1], "extension": row[2]} for row in file_data
        ]
    }
    path = f"{report_setup.REPORT_PATH}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Index report saved as JSON to {path}")

def save_text_report(file_data, log_entries):
    path = f"{report_setup.REPORT_PATH}.txt"
    with open(path, "w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(entry + "\n")
        f.write("\nFiles indexed:\n")
        for row in file_data:
            f.write(f"- {row[0]} ({row[1]}, {row[2]})\n")
    print(f"Index report saved as TXT to {path}")
