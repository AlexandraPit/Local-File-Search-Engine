DB_CONFIG = {
    "dbname": "filesystem",
    "user": "postgres",
    "password": "parola789",
    "host": "localhost",
    "port": "5432"
}
REPORT_FORMAT = None
REPORT_PATH = "index_report"
def choose_report_format():
    global REPORT_FORMAT
    while True:
        choice = input("Choose report format (1 for text, 2 for JSON): ")
        if choice == "1":
            REPORT_FORMAT = "text"
            break
        elif choice == "2":
            REPORT_FORMAT = "json"
            break
        else:
            print("Invalid choice. Please choose 1 for text or 2 for JSON.")