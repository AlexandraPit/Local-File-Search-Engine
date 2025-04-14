import tkinter as tk

from controller.main_cotroller import Controller
from indexer.report_setup import choose_report_format
from searcher.search_logger import SearchLogger
from ui.ui import SearchApp

if __name__ == "__main__":
    choose_report_format()

    search_logger = SearchLogger()
    controller = Controller()
    controller.register_observer(search_logger)

    root = tk.Tk()
    app = SearchApp(root, controller, search_logger)
    root.mainloop()