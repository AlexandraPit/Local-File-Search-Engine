import os
from datetime import datetime

from previewer.file_type_checker import is_text_file, read_text_file

def crawl_files(root_path):
    files = []
    errors = []

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root_path)
            name = os.path.basename(full_path)
            extension = os.path.splitext(full_path)[1].lower()

            try:
                content = read_text_file(full_path) if is_text_file(full_path) else None
            except Exception as e:
                errors.append(f"Failed to read {full_path}: {e}")
                content = None

            try:
                modified_time = datetime.fromtimestamp(os.path.getmtime(full_path))
            except Exception as e:
                errors.append(f"Failed to get modified time for {full_path}: {e}")
                modified_time = None

            files.append((rel_path, name, extension, content, content or "", modified_time))

    return files, errors
