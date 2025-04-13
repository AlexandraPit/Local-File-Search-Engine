import tkinter as tk

from config import choose_report_format
from controller import Controller
from search_logger import SearchLogger
from ui import SearchApp

if __name__ == "__main__":
    choose_report_format()

    search_logger = SearchLogger()
    controller = Controller()
    controller.register_observer(search_logger)

    root = tk.Tk()
    app = SearchApp(root, controller, search_logger)
    root.mainloop()