import tkinter as tk

from controller.main_cotroller import Controller
from controller.proxy import ProxySearch
from searcher.search_logger import SearchLogger
from ui.ui import SearchApp

if __name__ == "__main__":
    #choose_report_format()

    search_logger = SearchLogger()
    controller = Controller()
    controller.register_observer(search_logger)

    cached_controller = ProxySearch(controller)

    root = tk.Tk()
    app = SearchApp(root, cached_controller, search_logger)
    root.mainloop()