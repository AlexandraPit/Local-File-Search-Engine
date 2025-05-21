import tkinter as tk

class WidgetFactory:
    def __init__(self):
        self.rules = [
            (self.is_log_files, self.create_log_widget),
            (self.is_image_files, self.create_gallery_widget),
        ]

    def get_widgets(self, results):
        return [creator() for condition, creator in self.rules if condition(results)]

    def is_log_files(self, results):
        return any(path.endswith(".log") for path, _ in results)

    def is_image_files(self, results):
        return sum(1 for path, _ in results if path.endswith(('.jpg', '.png', '.jpeg'))) >= 3

    def create_log_widget(self):
        return lambda frame: tk.Label(frame, text="Analyze Logs Widget").pack()

    def create_gallery_widget(self):
        return lambda frame: tk.Label(frame, text="View as Gallery Widget").pack()
